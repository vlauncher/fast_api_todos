import pytest
from fastapi.testclient import TestClient

def test_create_todo_success(client, test_user, auth_headers):
    response = client.post(
        "/api/v1/todos/",
        json={
            "title": "New Todo",
            "description": "New Description"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Todo"
    assert data["description"] == "New Description"
    assert data["is_completed"] is False
    assert data["is_archived"] is False
    assert data["user_id"] == test_user.id

def test_create_todo_without_description(client, test_user, auth_headers):
    response = client.post(
        "/api/v1/todos/",
        json={"title": "New Todo"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Todo"
    assert data["description"] is None

def test_create_todo_unauthorized(client):
    response = client.post(
        "/api/v1/todos/",
        json={"title": "New Todo"}
    )
    assert response.status_code == 401

def test_get_todos(client, test_user, auth_headers, test_todo):
    response = client.get("/api/v1/todos/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(todo["id"] == test_todo.id for todo in data)

def test_get_todos_with_pagination(client, test_user, auth_headers):
    for i in range(5):
        client.post(
            "/api/v1/todos/",
            json={"title": f"Todo {i}"},
            headers=auth_headers
        )
    
    response = client.get("/api/v1/todos/?skip=0&limit=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_todos_archived_filter(db, client, test_user, auth_headers):
    from app.models import Todo
    
    todo1 = Todo(title="Active Todo", user_id=test_user.id)
    todo2 = Todo(title="Archived Todo", user_id=test_user.id, is_archived=True)
    db.add(todo1)
    db.add(todo2)
    db.commit()
    
    active_response = client.get("/api/v1/todos/?archived=false", headers=auth_headers)
    archived_response = client.get("/api/v1/todos/?archived=true", headers=auth_headers)
    
    assert active_response.status_code == 200
    assert archived_response.status_code == 200
    assert len(active_response.json()) >= 1
    assert len(archived_response.json()) >= 1

def test_get_todos_unauthorized(client):
    response = client.get("/api/v1/todos/")
    assert response.status_code == 401

def test_get_todo_by_id(client, test_user, auth_headers, test_todo):
    response = client.get(f"/api/v1/todos/{test_todo.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_todo.id
    assert data["title"] == test_todo.title

def test_get_todo_by_id_not_found(client, test_user, auth_headers):
    response = client.get("/api/v1/todos/99999", headers=auth_headers)
    assert response.status_code == 404
    assert "Todo not found" in response.json()["detail"]

def test_get_todo_by_id_unauthorized(client, test_todo):
    response = client.get(f"/api/v1/todos/{test_todo.id}")
    assert response.status_code == 401

def test_update_todo(client, test_user, auth_headers, test_todo):
    response = client.put(
        f"/api/v1/todos/{test_todo.id}",
        json={
            "title": "Updated Todo",
            "description": "Updated Description",
            "is_completed": True
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Todo"
    assert data["description"] == "Updated Description"
    assert data["is_completed"] is True

def test_update_todo_partial(client, test_user, auth_headers, test_todo):
    response = client.put(
        f"/api/v1/todos/{test_todo.id}",
        json={"title": "Updated Title"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == test_todo.description

def test_update_todo_not_found(client, test_user, auth_headers):
    response = client.put(
        "/api/v1/todos/99999",
        json={"title": "Updated"},
        headers=auth_headers
    )
    assert response.status_code == 404

def test_update_todo_unauthorized(client, test_todo):
    response = client.put(
        f"/api/v1/todos/{test_todo.id}",
        json={"title": "Updated"}
    )
    assert response.status_code == 401

def test_toggle_complete(client, test_user, auth_headers, test_todo):
    assert test_todo.is_completed is False
    
    response = client.patch(f"/api/v1/todos/{test_todo.id}/complete", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_completed"] is True
    
    response = client.patch(f"/api/v1/todos/{test_todo.id}/complete", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_completed"] is False

def test_toggle_complete_not_found(client, test_user, auth_headers):
    response = client.patch("/api/v1/todos/99999/complete", headers=auth_headers)
    assert response.status_code == 404

def test_toggle_complete_unauthorized(client, test_todo):
    response = client.patch(f"/api/v1/todos/{test_todo.id}/complete")
    assert response.status_code == 401

def test_toggle_archive(client, test_user, auth_headers, test_todo):
    assert test_todo.is_archived is False
    
    response = client.patch(f"/api/v1/todos/{test_todo.id}/archive", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_archived"] is True
    
    response = client.patch(f"/api/v1/todos/{test_todo.id}/archive", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["is_archived"] is False

def test_toggle_archive_not_found(client, test_user, auth_headers):
    response = client.patch("/api/v1/todos/99999/archive", headers=auth_headers)
    assert response.status_code == 404

def test_toggle_archive_unauthorized(client, test_todo):
    response = client.patch(f"/api/v1/todos/{test_todo.id}/archive")
    assert response.status_code == 401

def test_delete_todo(client, test_user, auth_headers, test_todo):
    todo_id = test_todo.id
    response = client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == 200
    assert "Todo deleted successfully" in response.json()["message"]
    
    get_response = client.get(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_delete_todo_not_found(client, test_user, auth_headers):
    response = client.delete("/api/v1/todos/99999", headers=auth_headers)
    assert response.status_code == 404

def test_delete_todo_unauthorized(client, test_todo):
    response = client.delete(f"/api/v1/todos/{test_todo.id}")
    assert response.status_code == 401
