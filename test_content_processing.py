#!/usr/bin/env python3
"""
Test script for StudySahayak content processing functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.content_processor import ContentProcessor
from services.ai_service import AIService
from config import Config

def test_text_processing():
    """Test text content processing"""
    print("Testing text processing...")
    
    processor = ContentProcessor()
    ai_service = AIService()
    
    sample_text = """
    Machine learning is a subset of artificial intelligence that focuses on the development of algorithms 
    and statistical models that enable computer systems to improve their performance on a specific task 
    through experience. The core idea behind machine learning is to create systems that can automatically 
    learn and improve from data without being explicitly programmed for every scenario.
    
    There are three main types of machine learning: supervised learning, unsupervised learning, and 
    reinforcement learning. Supervised learning uses labeled training data to learn a mapping function 
    from input to output. Unsupervised learning finds patterns in data without labeled examples. 
    Reinforcement learning learns through interaction with an environment to maximize some reward signal.
    """
    
    try:
        # Process text
        processed = processor.process_text(sample_text)
        print(f"✓ Text processed successfully. Word count: {processed['metadata']['word_count']}")
        
        # Generate structured content
        structured = ai_service.generate_structured_content(processed['text'], 'text')
        
        if isinstance(structured, dict) and 'error' not in structured:
            print("✓ Structured content generated successfully")
            print(f"Title: {structured.get('title', 'N/A')}")
            print(f"Sections: {len(structured.get('main_sections', []))}")
        else:
            print("✗ Failed to generate structured content:", structured.get('error', 'Unknown error'))
        
    except Exception as e:
        print(f"✗ Text processing failed: {e}")

def test_configuration():
    """Test configuration and dependencies"""
    print("Testing configuration...")
    
    # Check API keys
    if Config.GEMINI_API_KEY:
        print("✓ Gemini API key configured")
    else:
        print("⚠ Gemini API key not configured - AI features will be limited")
    
    # Check optional dependencies
    try:
        import whisper
        print("✓ Whisper available for better video transcription")
    except ImportError:
        print("⚠ Whisper not available - using basic speech recognition")
    
    try:
        import pdfplumber
        print("✓ pdfplumber available for better PDF extraction")
    except ImportError:
        print("⚠ pdfplumber not available - using basic PDF extraction")

def main():
    """Run all tests"""
    print("StudySahayak Content Processing Test")
    print("=" * 50)
    
    test_configuration()
    print()
    test_text_processing()
    print()
    print("Test completed!")

if __name__ == "__main__":
    main()
