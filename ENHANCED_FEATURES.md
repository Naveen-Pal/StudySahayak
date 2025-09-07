# StudySahayak - Enhanced Content Processing Features

## Overview of New Features

StudySahayak now provides comprehensive content processing capabilities that transform various types of input into well-structured educational materials using AI.

## Content Processing Pipeline

### 1. Video Content Processing
- **Input**: Video files (MP4, AVI, MOV, MKV, WebM, FLV, WMV)
- **Process**: 
  1. Extract audio from video using moviepy/ffmpeg
  2. Transcribe audio to text using:
     - OpenAI Whisper (preferred - high accuracy)
     - Google Speech Recognition (fallback)
     - Local speech recognition (final fallback)
  3. Generate structured content using AI
- **Output**: Comprehensive educational material with sections, key points, glossary

### 2. PDF Content Processing
- **Input**: PDF documents
- **Process**:
  1. Extract text using:
     - pdfplumber (preferred - better for complex layouts)
     - PyPDF2 (fallback - basic extraction)
  2. Clean and process extracted text
  3. Generate structured content using AI
- **Output**: Well-organized educational material

### 3. Text Content Processing
- **Input**: Raw text content
- **Process**:
  1. Clean and validate text input
  2. Direct AI structuring
- **Output**: Comprehensive structured educational content

## AI-Generated Structured Content Features

Each processed content includes:

### Executive Summary
- Brief overview of the main topic
- Context and background information

### Introduction
- Detailed introduction with context
- Background information

### Main Content Sections
- Logically organized sections
- Key points for each section
- Detailed explanations and examples

### Key Takeaways
- Important points to remember
- Main learning objectives

### Concepts Glossary
- Important terms and definitions
- Technical vocabulary explanations

### Conclusion
- Summary of main points
- Final thoughts and insights

### Metadata
- Content type information
- Estimated reading time
- Processing details (transcription method, extraction method)

## Installation and Setup

### Basic Installation
```bash
pip install -r requirements.txt
```

### Enhanced Installation (Recommended)
```bash
# Run the enhanced setup script
./setup_enhanced.sh
```

This will install:
- **pdfplumber**: Better PDF text extraction
- **OpenAI Whisper** (optional): Superior video transcription
- **System dependencies check**: Verifies ffmpeg availability

### Manual Enhanced Installation
```bash
# Better PDF processing
pip install pdfplumber

# Better video transcription (large download ~2.9GB)
pip install openai-whisper

# System dependency (if not installed)
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

## API Usage Examples

### Upload and Process Video
```bash
curl -X POST http://localhost:5000/api/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "type=video" \
  -F "file=@lecture_video.mp4"
```

### Upload and Process PDF
```bash
curl -X POST http://localhost:5000/api/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "type=pdf" \
  -F "file=@research_paper.pdf"
```

### Process Text Content
```bash
curl -X POST http://localhost:5000/api/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "type=text" \
  -F "content=Machine learning is a subset of artificial intelligence..."
```

### Get Structured Content
```bash
curl -X GET http://localhost:5000/api/content/CONTENT_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Frontend Features

### Enhanced Dashboard
- Visual content type indicators
- Processing status information
- Drag-and-drop file upload
- Real-time file validation

### Structured Content Viewer
- Navigate through: `/structured/CONTENT_ID`
- Comprehensive content display with:
  - Color-coded sections
  - Expandable key points
  - Glossary definitions
  - Metadata information
  - Print-friendly formatting

### Content Options
- Four main options:
  1. **Structured Content**: View organized material
  2. **Summary**: Generate concise summaries
  3. **Notes**: Create structured study notes
  4. **Quiz**: Generate interactive quizzes

## Configuration

Ensure your `.env` file includes:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URI=mongodb://localhost:27017/studysahayak
SERP_API_KEY=your_serp_api_key_here  # Optional for web search enhancement
```

## Testing

Run the enhanced functionality test:
```bash
python test_content_processing.py
```

This will verify:
- Configuration status
- API key availability
- Optional dependencies
- Text processing functionality
- AI structuring capabilities

## Performance Notes

### Video Processing
- Processing time depends on video length and transcription method
- Whisper: More accurate but slower
- Google Speech Recognition: Faster but requires internet
- Large videos may take several minutes to process

### PDF Processing
- Complex PDFs with images/tables may have extraction limitations
- pdfplumber handles most layouts better than PyPDF2
- Very large PDFs may require additional processing time

### AI Structuring
- Processing time depends on content length
- Gemini API rate limits may apply
- Structured content generation typically takes 10-30 seconds

## Troubleshooting

### Common Issues

1. **Video transcription fails**
   - Ensure ffmpeg is installed
   - Check audio quality in video
   - Verify internet connection for Google Speech Recognition

2. **PDF text extraction incomplete**
   - Install pdfplumber: `pip install pdfplumber`
   - Some PDFs with complex layouts may have limitations

3. **AI structuring fails**
   - Verify Gemini API key is configured
   - Check API quota and rate limits
   - Ensure content is not empty

4. **File upload errors**
   - Check file size limits
   - Verify file format is supported
   - Ensure sufficient disk space

## Future Enhancements

- Support for additional video formats
- OCR capabilities for image-based PDFs
- Real-time processing status updates
- Batch processing capabilities
- Custom AI prompts for structuring
- Multi-language content processing
