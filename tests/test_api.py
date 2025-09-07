import pytest
import json
import tempfile
import os
from app import app
from database import Database

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers(client):
    """Get authentication headers for testing"""
    # Register a test user
    register_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    client.post('/api/auth/register', json=register_data)
    
    # Login to get token
    login_response = client.post('/api/auth/login', json=register_data)
    token = json.loads(login_response.data)['access_token']
    
    return {'Authorization': f'Bearer {token}'}

class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'password': 'password123'
        }
        response = client.post('/api/auth/register', json=data)
        assert response.status_code == 201
        assert 'user_id' in json.loads(response.data)
    
    def test_register_missing_fields(self, client):
        """Test registration with missing fields"""
        data = {'username': 'testuser'}
        response = client.post('/api/auth/register', json=data)
        assert response.status_code == 400
    
    def test_login_success(self, client):
        """Test successful login"""
        # First register
        register_data = {
            'username': 'loginuser',
            'password': 'password123'
        }
        client.post('/api/auth/register', json=register_data)
        
        # Then login
        response = client.post('/api/auth/login', json=register_data)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'user_id' in data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        data = {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        }
        response = client.post('/api/auth/login', json=data)
        assert response.status_code == 401

class TestContent:
    """Test content-related endpoints"""
    
    def test_upload_text_content(self, client, auth_headers):
        """Test uploading text content"""
        data = {
            'type': 'text',
            'content': 'This is a test content for processing.'
        }
        response = client.post('/api/upload', data=data, headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'content_id' in data
        assert 'title' in data
    
    def test_upload_invalid_type(self, client, auth_headers):
        """Test uploading with invalid content type"""
        data = {
            'type': 'invalid',
            'content': 'test content'
        }
        response = client.post('/api/upload', data=data, headers=auth_headers)
        assert response.status_code == 400
    
    def test_list_content(self, client, auth_headers):
        """Test listing user content"""
        # First upload some content
        data = {
            'type': 'text',
            'content': 'Test content for listing'
        }
        client.post('/api/upload', data=data, headers=auth_headers)
        
        # Then list content
        response = client.get('/api/list', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'contents' in data
        assert len(data['contents']) > 0
    
    def test_generate_summary(self, client, auth_headers):
        """Test generating summary"""
        # First upload content
        upload_data = {
            'type': 'text',
            'content': 'This is a comprehensive test content that discusses various aspects of machine learning and artificial intelligence.'
        }
        upload_response = client.post('/api/upload', data=upload_data, headers=auth_headers)
        content_id = json.loads(upload_response.data)['content_id']
        
        # Generate summary
        summary_data = {
            'content_id': content_id,
            'language': 'english'
        }
        response = client.post('/api/summary', json=summary_data, headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'summary' in data
    
    def test_generate_quiz(self, client, auth_headers):
        """Test generating quiz"""
        # First upload content
        upload_data = {
            'type': 'text',
            'content': 'Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models.'
        }
        upload_response = client.post('/api/upload', data=upload_data, headers=auth_headers)
        content_id = json.loads(upload_response.data)['content_id']
        
        # Generate quiz
        quiz_data = {
            'content_id': content_id,
            'language': 'english',
            'num_questions': 5
        }
        response = client.post('/api/quiz', json=quiz_data, headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'quiz' in data
    
    def test_generate_notes(self, client, auth_headers):
        """Test generating notes"""
        # First upload content
        upload_data = {
            'type': 'text',
            'content': 'Python is a high-level programming language known for its simplicity and readability.'
        }
        upload_response = client.post('/api/upload', data=upload_data, headers=auth_headers)
        content_id = json.loads(upload_response.data)['content_id']
        
        # Generate notes
        notes_data = {
            'content_id': content_id,
            'language': 'english'
        }
        response = client.post('/api/notes', json=notes_data, headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'notes' in data

class TestSecurity:
    """Test security and authorization"""
    
    def test_unauthorized_access(self, client):
        """Test accessing protected endpoints without authentication"""
        response = client.get('/api/list')
        assert response.status_code == 401
        
        response = client.post('/api/upload', data={'type': 'text', 'content': 'test'})
        assert response.status_code == 401
    
    def test_invalid_token(self, client):
        """Test accessing with invalid token"""
        headers = {'Authorization': 'Bearer invalid-token'}
        response = client.get('/api/list', headers=headers)
        assert response.status_code == 422  # Unprocessable Entity for invalid JWT

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
