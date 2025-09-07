import os
from werkzeug.utils import secure_filename
from config import Config

def validate_upload(file, content_type):
    """Validate uploaded file"""
    
    if not file or file.filename == '':
        return {'valid': False, 'error': 'No file provided'}
    
    filename = secure_filename(file.filename)
    if not filename:
        return {'valid': False, 'error': 'Invalid filename'}
    
    # Check file extension
    file_ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    if content_type == 'video':
        if file_ext not in Config.ALLOWED_VIDEO_EXTENSIONS:
            return {
                'valid': False, 
                'error': f'Invalid video format. Allowed: {", ".join(Config.ALLOWED_VIDEO_EXTENSIONS)}'
            }
    elif content_type == 'pdf':
        if file_ext not in Config.ALLOWED_PDF_EXTENSIONS:
            return {
                'valid': False, 
                'error': f'Invalid PDF format. Allowed: {", ".join(Config.ALLOWED_PDF_EXTENSIONS)}'
            }
    
    return {'valid': True}

def validate_content_request(data, required_fields):
    """Validate request data"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        return {
            'valid': False, 
            'error': f'Missing required fields: {", ".join(missing_fields)}'
        }
    
    return {'valid': True}

def allowed_file(filename, file_type):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'video':
        return ext in Config.ALLOWED_VIDEO_EXTENSIONS
    elif file_type == 'pdf':
        return ext in Config.ALLOWED_PDF_EXTENSIONS
    
    return False
