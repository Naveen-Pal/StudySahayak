import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # MongoDB settings
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb+srv://naveen:sahayakpassdb@study.ifzehng.mongodb.net/?retryWrites=true&w=majority&appName=study'
    MONGO_DB_NAME = 'study'
    MONGO_COLLECTION_NAME = 'info'
    
    # Gemini API settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or ''
    
    # File upload settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}
    ALLOWED_PDF_EXTENSIONS = {'pdf'}
    
    # Search API settings (SerpAPI for web search)
    SERP_API_KEY = os.environ.get('SERP_API_KEY') or ''
