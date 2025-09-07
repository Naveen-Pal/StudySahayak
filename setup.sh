#!/bin/bash

# StudySahayak API Setup Script

echo "Setting up StudySahayak API..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create uploads directory
echo "Creating uploads directory..."
mkdir -p uploads

# Create .env file from example
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your API keys before running the application."
fi

# Make sure MongoDB is accessible (you may need to start MongoDB service)
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - GEMINI_API_KEY (required for AI features)"
echo "   - SERP_API_KEY (optional for web search enhancement)"
echo "2. Install system dependencies:"
echo "   - sudo apt-get install ffmpeg (for video processing)"
echo "   - sudo apt-get install portaudio19-dev (for speech recognition)"
echo "3. Run the application: python app.py"
echo ""
echo "API will be available at: http://localhost:5000"
echo "API Documentation: See API_DOCUMENTATION.md"
