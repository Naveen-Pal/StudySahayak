# StudySahayak - AI-Powered Content Repurposing & Localization

## Project Overview
StudySahayak is an AI-powered system that transforms existing content (lectures, case studies, assignments) into multiple formats including summaries, interactive quizzes, and structured notes in various languages.

## Features
- **Content Upload**: Support for text, PDF, and video content
- **AI Processing**: Automatic content enhancement using Google Gemini API
- **Multi-format Output**: Generate summaries, quizzes, and structured notes
- **Multi-language Support**: Content localization in various languages
- **Video Transcription**: Automatic transcription using Google Speech Recognition
- **JWT Authentication**: Secure user authentication and authorization
- **MongoDB Integration**: Scalable document storage

## Technology Stack
- **Backend**: Flask (Python)
- **Database**: MongoDB
- **AI Services**: Google Gemini API, Google Speech Recognition
- **Authentication**: JWT (JSON Web Tokens)
- **File Processing**: PyPDF2, MoviePy, SpeechRecognition

## Project Structure
```
StudySahayak/
├── app.py                    # Main Flask application
├── config.py                # Configuration settings
├── database.py              # MongoDB operations
├── requirements.txt         # Python dependencies
├── setup.sh                 # Setup script
├── .env.example             # Environment variables template
├── API_DOCUMENTATION.md     # API documentation
├── services/
│   ├── __init__.py
│   ├── ai_service.py        # AI/LLM service integration
│   └── content_processor.py # Content processing service
├── utils/
│   ├── __init__.py
│   └── validators.py        # Input validation utilities
└── tests/
    └── test_api.py          # API tests
```

## Quick Start

### 1. Setup Environment
```bash
# Clone the repository (if using git)
git clone <repository-url>
cd StudySahayak

# Run setup script
chmod +x setup.sh
./setup.sh
```

### 2. Configure Environment Variables
Edit the `.env` file with your API keys:
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

Required API keys:
- `GEMINI_API_KEY`: Google Gemini API key for AI features
- `SERP_API_KEY`: SerpAPI key for web search enhancement (optional)

### 3. Install System Dependencies
```bash
# Install FFmpeg for video processing
sudo apt-get update
sudo apt-get install ffmpeg

# Install PortAudio for speech recognition
sudo apt-get install portaudio19-dev
```

### 4. Run the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Run the Flask app
python app.py
```

The API will be available at `http://localhost:5000`

## API Usage Examples

### 1. Register and Login
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

### 2. Upload Text Content
```bash
curl -X POST http://localhost:5000/api/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "type=text" \
  -F "content=Your text content here..."
```

### 3. Upload PDF File
```bash
curl -X POST http://localhost:5000/api/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "type=pdf" \
  -F "file=@document.pdf"
```

### 4. Generate Summary
```bash
curl -X POST http://localhost:5000/api/summary \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content_id": "CONTENT_ID", "language": "english"}'
```

### 5. Generate Quiz
```bash
curl -X POST http://localhost:5000/api/quiz \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content_id": "CONTENT_ID", "language": "english", "num_questions": 10}'
```

## Testing
```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=.
```

## Configuration Options

### Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key | Yes |
| `JWT_SECRET_KEY` | JWT signing key | Yes |
| `MONGO_URI` | MongoDB connection string | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `SERP_API_KEY` | SerpAPI key for web search | No |

### File Upload Limits
- Maximum file size: 50MB
- Supported video formats: mp4, avi, mov, wmv, flv, webm
- Supported document formats: pdf

## Development

### Adding New Features
1. Add new endpoints in `app.py`
2. Add business logic in appropriate service files
3. Update tests in `tests/test_api.py`
4. Update API documentation

### Database Schema
The MongoDB collections used:
- `users`: User authentication data
- `info`: Content storage with metadata

## Deployment Considerations
1. Set strong secret keys in production
2. Use environment-specific MongoDB clusters
3. Configure proper CORS settings
4. Set up SSL/TLS encryption
5. Implement rate limiting
6. Set up monitoring and logging

## Troubleshooting

### Common Issues
1. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
2. **FFmpeg not found**: Install FFmpeg system package with `sudo apt-get install ffmpeg`
3. **PortAudio errors**: Install PortAudio with `sudo apt-get install portaudio19-dev`
4. **MongoDB connection**: Check MongoDB URI and network connectivity
5. **API key errors**: Verify API keys in `.env` file
6. **Speech recognition errors**: Ensure microphone permissions and audio file quality

### Logs
Check application logs for detailed error information. The application uses Python logging for debugging.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License
This project is licensed under the MIT License.

## API Documentation
Detailed API documentation is available in `API_DOCUMENTATION.md`.
