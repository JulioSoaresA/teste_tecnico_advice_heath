import os
import pytest
from app import app, db

# Fixture do cliente de teste
@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://user:password@localhost:3306/todolistapp_test"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'teste_key' 

    with app.app_context():
        db.create_all()  # Cria as tabelas
        yield app.test_client()  # Retorna o cliente de teste
        db.drop_all()  # Remove as tabelas após os testes

def test_user_registration_existing_username(test_client):
    # Primeiro, registre um usuário
    test_client.post('/register', data={'user': 'existinguser', 'senha': 'password123'})
    
    
    # Tente registrar o mesmo usuário novamente
    response = test_client.post('/register', data={'user': 'existinguser', 'senha': 'password456'})
    
    # Verifica se a mensagem de erro é retornada
    assert response.status_code == 302  # Redirecionamento
    with test_client.session_transaction() as session:
        assert 'Usuário já existe. Escolha outro nickname.' in dict(session['_flashes']).values()


def test_user_login(test_client):
    # Primeiro, registre um usuário
    test_client.post('/register', data={'user': 'loginuser', 'senha': 'password123'})
    
    # Tente fazer login
    response = test_client.post('/login', data={'user': 'loginuser', 'senha': 'password123'})
    
    # Verifica se o redirecionamento ocorreu
    assert response.status_code == 302  # Redirecionamento
    with test_client.session_transaction() as session:
        assert 'loginuser logado com sucesso!' in dict(session['_flashes']).values()


def test_user_login_invalid_credentials(test_client):
    # Tente fazer login com um usuário que não existe
    response = test_client.post('/login', data={'user': 'invaliduser', 'senha': 'wrongpassword'})
    
    # Verifica se uma mensagem de erro é retornada
    assert response.status_code == 302  # Redirecionamento
    with test_client.session_transaction() as session:
        assert 'Usuário ou senha incorretos.' in dict(session['_flashes']).values()


def test_create_car(test_client):
    # Registre e faça login de um usuário
    test_client.post('/register', data={'user': 'caruser', 'senha': 'password123'})
    test_client.post('/login', data={'user': 'caruser', 'senha': 'password123'})
    
    # Crie um carro
    response = test_client.post('/create_car', data={'owner_id': 1, 'model': 'sedan', 'color': 'blue'})
    
    # Verifica se a criação do carro foi bem-sucedida
    assert response.status_code == 302  # Redirecionamento
    with test_client.session_transaction() as session:
        assert 'Carro cadastrado com sucesso!' in dict(session['_flashes']).values()


def test_create_car_limit_reached(test_client):
    # Registre e faça login de um usuário
    test_client.post('/register', data={'user': 'limituser', 'senha': 'password123'})
    test_client.post('/login', data={'user': 'limituser', 'senha': 'password123'})
    
    # Crie 3 carros para atingir o limite
    for i in range(3):
        test_client.post('/create_car', data={'owner_id': 1, 'model': 'sedan', 'color': 'blue'})
    
    # Tente criar um quarto carro
    response = test_client.post('/create_car', data={'owner_id': 1, 'model': 'sedan', 'color': 'gray'})
    
    # Verifica se a mensagem de erro de limite é retornada
    assert response.status_code == 302  # Redirecionamento
    with test_client.session_transaction() as session:
        assert 'Você já tem 3 carros cadastrados. Limite atingido.' in dict(session['_flashes']).values()
