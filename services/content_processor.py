import os
import subprocess
import tempfile
from PIL import Image
import PyPDF2
import requests
from io import BytesIO
import logging
from config import Config
import speech_recognition as sr
import moviepy.editor as mp

class ContentProcessor:
    """Service for processing different types of content"""
    
    def __init__(self):
        self.serp_api_key = Config.SERP_API_KEY
    
    def process_text(self, text_content):
        """Process raw text content"""
        try:
            # Basic text cleaning and formatting
            cleaned_text = self._clean_text(text_content)
            
            return {
                'text': cleaned_text,
                'metadata': {
                    'word_count': len(cleaned_text.split()),
                    'character_count': len(cleaned_text),
                    'type': 'text'
                }
            }
            
        except Exception as e:
            logging.error(f"Error processing text: {e}")
            raise Exception(f"Failed to process text content: {str(e)}")
    
    def process_pdf(self, file_path):
        """Extract text from PDF file using multiple methods"""
        try:
            text_content = ""
            
            # Try PyPDF2 first
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    page_count = len(pdf_reader.pages)
                    
                    for page_num in range(page_count):
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text.strip():  # Only add non-empty pages
                            text_content += page_text + "\n"
            except Exception as e:
                logging.warning(f"PyPDF2 extraction failed: {e}, trying alternative method")
                text_content = self._extract_pdf_with_pdfplumber(file_path)
            
            # Clean the extracted text
            cleaned_text = self._clean_text(text_content)
            
            if not cleaned_text.strip():
                raise Exception("No text could be extracted from the PDF")
            
            return {
                'text': cleaned_text,
                'metadata': {
                    'page_count': page_count if 'page_count' in locals() else 'unknown',
                    'word_count': len(cleaned_text.split()),
                    'character_count': len(cleaned_text),
                    'type': 'pdf',
                    'extraction_method': 'PyPDF2'
                }
            }
            
        except Exception as e:
            logging.error(f"Error processing PDF: {e}")
            raise Exception(f"Failed to process PDF file: {str(e)}")
    
    def _extract_pdf_with_pdfplumber(self, file_path):
        """Alternative PDF extraction using pdfplumber (better for complex layouts)"""
        try:
            import pdfplumber
            
            text_content = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
            
            return text_content
            
        except ImportError:
            logging.warning("pdfplumber not available, using basic extraction")
            # Fallback to basic text extraction if pdfplumber is not available
            return self._basic_pdf_extraction(file_path)
        except Exception as e:
            logging.error(f"pdfplumber extraction failed: {e}")
            return self._basic_pdf_extraction(file_path)
    
    def _basic_pdf_extraction(self, file_path):
        """Basic PDF text extraction fallback"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
                
                return text_content
        except Exception as e:
            logging.error(f"Basic PDF extraction failed: {e}")
            return "Failed to extract text from PDF file."
    
    def process_video(self, file_path):
        """Process video file - extract audio and transcribe"""
        try:
            # Extract audio from video
            audio_path = self._extract_audio_from_video(file_path)
            
            # Transcribe audio to text
            transcription = self._transcribe_audio(audio_path)
            
            # Clean up temporary audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            # Clean the transcribed text
            cleaned_text = self._clean_text(transcription)
            
            return {
                'text': cleaned_text,
                'metadata': {
                    'word_count': len(cleaned_text.split()),
                    'character_count': len(cleaned_text),
                    'type': 'video',
                    'transcription_source': 'whisper'
                }
            }
            
        except Exception as e:
            logging.error(f"Error processing video: {e}")
            raise Exception(f"Failed to process video file: {str(e)}")
    
    def _extract_audio_from_video(self, video_path):
        """Extract audio from video file using moviepy"""
        try:
            # Create temporary file for audio
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            audio_path = temp_audio.name
            temp_audio.close()
            
            # Use moviepy to extract audio
            video = mp.VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(audio_path, verbose=False, logger=None)
            
            # Clean up
            audio.close()
            video.close()
            
            return audio_path
            
        except Exception as e:
            logging.error(f"Error extracting audio with moviepy: {e}")
            # Fallback to ffmpeg if moviepy fails
            return self._extract_audio_with_ffmpeg(video_path)
    
    def _extract_audio_with_ffmpeg(self, video_path):
        """Fallback method to extract audio using ffmpeg"""
        try:
            # Create temporary file for audio
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            audio_path = temp_audio.name
            temp_audio.close()
            
            # Use ffmpeg to extract audio
            command = [
                'ffmpeg', '-i', video_path, 
                '-vn',  # No video
                '-acodec', 'pcm_s16le',  # Audio codec
                '-ar', '16000',  # Sample rate
                '-ac', '1',  # Mono channel
                '-y',  # Overwrite output file
                audio_path
            ]
            
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
            
            return audio_path
            
        except Exception as e:
            logging.error(f"Error extracting audio: {e}")
            raise Exception(f"Failed to extract audio from video: {str(e)}")
    
    def _transcribe_audio(self, audio_path):
        """Transcribe audio using multiple methods (Whisper preferred, fallback to Google Speech Recognition)"""
        try:
            # Try using OpenAI Whisper first (if available)
            whisper_result = self._transcribe_with_whisper(audio_path)
            if whisper_result and len(whisper_result.strip()) > 0:
                return whisper_result
        except Exception as e:
            logging.warning(f"Whisper transcription failed: {e}, trying Google Speech Recognition")
        
        try:
            # Fallback to Google Speech Recognition
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source)
                # Record the audio
                audio = recognizer.record(source)
            
            # Use Google Speech Recognition (free tier)
            text = recognizer.recognize_google(audio)
            return text
            
        except sr.UnknownValueError:
            logging.warning("Speech recognition could not understand audio")
            return "Audio transcription failed - speech not clearly audible."
        except sr.RequestError as e:
            logging.error(f"Could not request results from Google Speech Recognition service: {e}")
            # Fallback to local speech recognition if available
            return self._transcribe_with_local_recognition(audio_path)
        except Exception as e:
            logging.error(f"Error transcribing audio: {e}")
            return "Audio transcription failed. Please check audio quality."
    
    def _transcribe_with_whisper(self, audio_path):
        """Transcribe audio using OpenAI Whisper (if installed)"""
        try:
            import whisper
            
            # Load the model (base model for balance of speed and accuracy)
            model = whisper.load_model("base")
            
            # Transcribe the audio
            result = model.transcribe(audio_path)
            
            return result["text"]
            
        except ImportError:
            logging.info("Whisper not installed, falling back to other methods")
            return None
        except Exception as e:
            logging.error(f"Whisper transcription error: {e}")
            return None
    
    def _transcribe_with_local_recognition(self, audio_path):
        """Fallback transcription using offline speech recognition"""
        try:
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
            
            # Try offline recognition (requires additional setup)
            # This is a fallback and may not work without proper setup
            text = recognizer.recognize_sphinx(audio)
            return text
            
        except Exception as e:
            logging.error(f"Local speech recognition error: {e}")
            return "Audio transcription service temporarily unavailable."
    
    def _clean_text(self, text):
        """Clean and format text content"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove special characters that might cause issues
        text = text.replace('\x00', '')  # Remove null characters
        
        # Basic formatting
        text = text.strip()
        
        return text
