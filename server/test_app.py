# test_app.py

import pytest
from app import create_app, db
from app.models import User


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()

    # Configure the app for testing
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # Use an in-memory SQLite database for tests
    })

    # Create a context for the app and initialize the database
    with flask_app.app_context():
        db.create_all()  # Ensure all tables are created

    # Provide the test client for the app
    yield flask_app.test_client()

    # Cleanup after tests
    with flask_app.app_context():
        db.drop_all()

def test_register_user(test_client):
    response = test_client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })

    assert response.status_code == 201
    assert b"User registered successfully!" in response.data

def test_login_user(test_client):
    # Регистрируем пользователя
    test_client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })

    # Пытаемся войти
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })

    assert response.status_code == 200
    assert 'access_token' in response.json

def test_create_chat(test_client):
    # Регистрируем пользователя
    test_client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })

    # Логинимся и получаем токен
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    access_token = response.json['access_token']

    # Создаем заголовок с токеном
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Создаем новый чат
    response = test_client.post('/chats', headers=headers, json={
        'name': 'Test Chat',
        'type': 'group'
    })

    assert response.status_code == 201
    assert b"Chat created successfully!" in response.data

def test_send_message(test_client):
    # Регистрируем пользователя
    test_client.post('/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword'
    })

    # Логинимся и получаем токен
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    access_token = response.json['access_token']

    # Создаем заголовок с токеном
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Создаем новый чат
    chat_response = test_client.post('/chats', headers=headers, json={
        'name': 'Test Chat',
        'type': 'group'
    })
    chat_id = chat_response.json['chat_id']

    # Отправляем сообщение
    response = test_client.post('/messages', headers=headers, json={
        'chat_id': chat_id,
        'content': 'Hello, world!'
    })

    assert response.status_code == 201
    assert b"Message sent successfully!" in response.data
