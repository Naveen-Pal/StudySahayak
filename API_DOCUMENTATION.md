# StudySahayak API Documentation

## Overview
StudySahayak is an AI-Powered Content Processing & Structuring system that transforms content (videos, PDFs, text) into well-structured educational materials. The system features:

- **Video Processing**: Auto-transcription followed by AI structuring
- **PDF Processing**: Text extraction followed by AI structuring  
- **Text Processing**: Direct AI structuring of raw text
- **Multi-language Support**: Content generation in multiple languages
- **Multiple Output Formats**: Summaries, structured notes, quizzes

## Content Processing Flow

1. **Upload Content** → Raw content (video/PDF/text)
2. **Content Processing** → Extract/transcribe content to text
3. **AI Structuring** → Generate well-organized educational material
4. **Output Generation** → Create summaries, notes, quizzes

## Base URL
```
http://localhost:5000
```

## Authentication
All endpoints (except auth and health) require JWT authentication.
Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### 1. Authentication

#### Register User
**POST** `/api/auth/register`

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response (201):**
```json
{
    "message": "User created successfully",
    "user_id": "user_id_string"
}
```

#### Login
**POST** `/api/auth/login`

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response (200):**
```json
{
    "access_token": "jwt_token_string",
    "user_id": "user_id_string"
}
```

### 2. Content Management

#### Upload Content
**POST** `/api/upload`

This endpoint handles three types of content with intelligent processing:

**Form Data:**
- `type`: "text", "pdf", or "video"
- `content`: (for text type) - The text content
- `file`: (for pdf/video type) - The file upload

**Content Processing Details:**

1. **Video Content (`type: video`)**:
   - Supported formats: MP4, AVI, MOV, MKV, WebM, FLV, WMV
   - Process: Extract audio → Transcribe to text → AI structure generation
   - Transcription: Uses Whisper (if available) or Google Speech Recognition
   - Output: Fully structured educational content

2. **PDF Content (`type: pdf`)**:
   - Supported format: PDF files
   - Process: Extract text → AI structure generation
   - Extraction: Uses pdfplumber (if available) or PyPDF2
   - Output: Fully structured educational content

3. **Text Content (`type: text`)**:
   - Process: Direct AI structure generation
   - Output: Fully structured educational content

**Example for text:**
```
type: text
content: "Machine learning is a subset of artificial intelligence..."
```

**Example for video:**
```
type: video
file: [MP4 video file]
```

**Example for PDF:**
```
type: pdf
file: [PDF document]
```

**Response (201):**
```json
{
    "message": "Content uploaded and processed successfully",
    "content_id": "content_id_string",
    "title": "AI-Generated Comprehensive Title"
}
}
```

#### List User Content
**GET** `/api/list`

**Response (200):**
```json
{
    "contents": [
        {
            "_id": "content_id",
            "title": "Content Title",
            "content_type": "text",
            "created_at": "2023-09-07T10:30:00",
            "updated_at": "2023-09-07T10:30:00",
            "metadata": {
                "word_count": 150,
                "character_count": 800,
                "type": "text"
            }
        }
    ]
}
```

### 3. Content Management

#### Get Structured Content
**GET** `/api/content/{content_id}`

**Response (200):**
```json
{
    "content_id": "content_id",
    "title": "Content Title",
    "structured_content": {
        "title": "Comprehensive Title",
        "executive_summary": "Brief overview of the content",
        "introduction": "Introduction with context",
        "main_sections": [
            {
                "section_title": "Section 1: Main Topic",
                "content": "Detailed content for this section",
                "key_points": [
                    "Important point 1",
                    "Important point 2"
                ]
            }
        ],
        "key_takeaways": [
            "Main takeaway 1",
            "Main takeaway 2"
        ],
        "conclusion": "Summary and final thoughts",
        "concepts_glossary": {
            "concept1": "definition1",
            "concept2": "definition2"
        },
        "metadata": {
            "content_type": "video",
            "language": "english",
            "estimated_read_time": "5 minutes"
        }
    },
    "content_type": "video",
    "metadata": {
        "word_count": 1500,
        "transcription_source": "whisper"
    },
    "created_at": "2023-09-07T10:30:00"
}
```

#### Delete Content
**DELETE** `/api/content/{content_id}`

**Response (200):**
```json
{
    "message": "Content 'Content Title' has been deleted successfully",
    "content_id": "content_id"
}
```

**Response (404):**
```json
{
    "error": "Content not found or you do not have permission to delete it"
}
```

### 4. AI-Powered Features

#### Generate Summary
**POST** `/api/summary`

**Request Body:**
```json
{
    "content_id": "your_content_id",
    "language": "english"
}
```

**Response (200):**
```json
{
    "content_id": "content_id",
    "title": "Content Title",
    "summary": {
        "main_topic": "Topic of the content",
        "key_points": [
            "Key point 1",
            "Key point 2"
        ],
        "concepts": {
            "concept1": "definition1",
            "concept2": "definition2"
        },
        "conclusion": "Main conclusion"
    },
    "language": "english"
}
```

#### Generate Quiz
**POST** `/api/quiz`

**Request Body:**
```json
{
    "content_id": "your_content_id",
    "language": "english",
    "num_questions": 10
}
```

**Response (200):**
```json
{
    "content_id": "content_id",
    "title": "Content Title",
    "quiz": {
        "quiz_title": "Quiz Title",
        "total_questions": 10,
        "questions": [
            {
                "id": 1,
                "question": "What is machine learning?",
                "options": {
                    "A": "A type of computer",
                    "B": "A subset of AI",
                    "C": "A programming language",
                    "D": "A database"
                },
                "correct_answer": "B",
                "explanation": "Machine learning is indeed a subset of artificial intelligence."
            }
        ]
    },
    "language": "english",
    "total_questions": 10
}
```

#### Generate Notes
**POST** `/api/notes`

**Request Body:**
```json
{
    "content_id": "your_content_id",
    "language": "english"
}
```

**Response (200):**
```json
{
    "content_id": "content_id",
    "title": "Content Title",
    "notes": {
        "title": "Notes Title",
        "sections": [
            {
                "heading": "Introduction",
                "content": "• Key point 1\n• Key point 2",
                "key_concepts": ["concept1", "concept2"]
            }
        ],
        "summary": "Overall summary",
        "key_takeaways": [
            "Takeaway 1",
            "Takeaway 2"
        ]
    },
    "language": "english"
}
```

### 4. Health Check

#### Health Check
**GET** `/api/health`

**Response (200):**
```json
{
    "status": "healthy",
    "service": "StudySahayak API"
}
```

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request:**
```json
{
    "error": "Error message describing what went wrong"
}
```

**401 Unauthorized:**
```json
{
    "error": "Missing or invalid authentication token"
}
```

**404 Not Found:**
```json
{
    "error": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
    "error": "Internal server error message"
}
```

## Supported Languages
The API supports content generation in multiple languages. Common language options include:
- english
- hindi
- spanish
- french
- german
- chinese
- japanese
- arabic

## File Upload Limits
- Maximum file size: 50MB
- Supported video formats: mp4, avi, mov, wmv, flv, webm
- Supported document formats: pdf

## Notes
1. Video files are transcribed using Google Speech Recognition (free service)
2. AI features use Google Gemini API (requires Gemini API key)
3. Text content can be enhanced with web search results using SerpAPI (optional)
4. All timestamps are in UTC format
5. Content is automatically processed and enhanced using AI
