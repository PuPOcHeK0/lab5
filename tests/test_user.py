from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]

def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]

def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'unexisted@mail.com'})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user = {
        'name': 'New User',
        'email': 'new.user@mail.com',
    }
    response = client.post("/api/v1/user", json=new_user)
    # Эндпоинт создания возвращает 201 и id созданного пользователя (int)
    assert response.status_code == 201
    assert isinstance(response.json(), int)
    # Проверяем, что пользователь действительно появился в БД
    check = client.get("/api/v1/user", params={'email': new_user['email']})
    assert check.status_code == 200
    assert check.json()['name'] == new_user['name']
    assert check.json()['email'] == new_user['email']

def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    duplicate_user = {
        'name': 'Duplicate User',
        'email': users[0]['email'],  # эта почта уже занята Ivan Ivanov
    }
    response = client.post("/api/v1/user", json=duplicate_user)
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}

def test_delete_user():
    '''Удаление пользователя'''
     # Создаём отдельного пользователя, которого будем удалять
    temp_user = {
        'name': 'Temp User',
        'email': 'temp.user@mail.com',
    }
    create_response = client.post("/api/v1/user", json=temp_user)
    assert create_response.status_code == 201
 
    # Удаляем его и ожидаем 204 (No Content)
    response = client.delete("/api/v1/user", params={'email': temp_user['email']})
    assert response.status_code == 204
 
    # Проверяем, что пользователь больше не находится в БД
    check = client.get("/api/v1/user", params={'email': temp_user['email']})
    assert check.status_code == 404
