#!/bin/bash

# Enhanced StudySahayak Setup Script
# This script installs additional dependencies for better content processing

echo "StudySahayak Enhanced Setup"
echo "=========================="

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✓ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠ Warning: No virtual environment detected. It's recommended to use one."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Installing enhanced dependencies..."

# Install basic requirements
echo "Installing basic requirements..."
pip install -r requirements.txt

# Install optional dependencies for better functionality
echo ""
echo "Installing optional dependencies for enhanced functionality..."

# pdfplumber for better PDF extraction
echo "Installing pdfplumber for better PDF text extraction..."
pip install pdfplumber==0.9.0

# Ask about Whisper installation (it's large)
echo ""
echo "OpenAI Whisper provides much better video transcription but requires ~2.9GB of space."
read -p "Install OpenAI Whisper for better video transcription? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing OpenAI Whisper..."
    pip install openai-whisper
    echo "✓ Whisper installed successfully"
else
    echo "⚠ Skipping Whisper installation. Video transcription will use basic speech recognition."
fi

# System dependencies check
echo ""
echo "Checking system dependencies..."

# Check for ffmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✓ ffmpeg is available"
else
    echo "⚠ ffmpeg not found. Install it for better video processing:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/"
fi

echo ""
echo "Setup completed!"
echo ""
echo "Enhanced features available:"
echo "✓ Better PDF text extraction (pdfplumber)"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "✓ Enhanced video transcription (Whisper)"
fi
echo "✓ AI-powered structured content generation"
echo "✓ Multiple content type support (video, PDF, text)"
echo ""
echo "Run the application with: python app.py"
echo "Test the enhanced features with: python test_content_processing.py"
