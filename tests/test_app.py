import os
import tempfile
import pytest

from app import app, init_db, DB_NAME

@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Controle de Recepcao' in response.data or b'Controle de Recep\xc3\xa7\xc3\xa3o' in response.data

def test_register_member(client):
    response = client.post('/register', data={
        'name': 'Carlos Silva',
        'plan': 'Mensal'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Carlos Silva' in response.data
    assert b'Mensal' in response.data