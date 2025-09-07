from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_file
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
import logging
from datetime import timedelta
import uuid
from config import Config
from database import Database
from services.content_processor import ContentProcessor
from services.ai_service import AIService
from services.pdf_generator import PDFGenerator
from utils.validators import validate_upload, validate_content_request
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Initialize JWT
jwt = JWTManager(app)

# Add custom Jinja2 filters
def nl2br(value):
    """Convert newlines to HTML line breaks"""
    if value is None:
        return ''
    import re
    # Clean any remaining markdown syntax
    value = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', value)  # Bold
    value = re.sub(r'\*(.*?)\*', r'<em>\1</em>', value)  # Italic
    value = re.sub(r'#{1,6}\s*', '', value)  # Remove markdown headers
    value = re.sub(r'```.*?```', '', value, flags=re.DOTALL)  # Remove code blocks
    # Convert newlines to HTML breaks
    return value.replace('\n', '<br>\n')

app.jinja_env.filters['nl2br'] = nl2br

# Initialize services
db = Database()
content_processor = ContentProcessor()
ai_service = AIService()
pdf_generator = PDFGenerator()

def extract_text_from_content(content_data):
    """Extract raw text from content data (handles both structured and raw text)"""
    if isinstance(content_data, str):
        try:
            # Try to parse as JSON first
            parsed_content = json.loads(content_data)
            if isinstance(parsed_content, dict):
                # If it's structured content, extract text from various sections
                text_parts = []
                
                # Add executive summary
                if 'executive_summary' in parsed_content:
                    text_parts.append(parsed_content['executive_summary'])
                
                # Add introduction
                if 'introduction' in parsed_content:
                    text_parts.append(parsed_content['introduction'])
                
                # Add main sections content
                if 'main_sections' in parsed_content:
                    for section in parsed_content['main_sections']:
                        if 'content' in section:
                            text_parts.append(section['content'])
                
                # Add conclusion
                if 'conclusion' in parsed_content:
                    text_parts.append(parsed_content['conclusion'])
                
                # If we extracted parts, join them
                if text_parts:
                    return ' '.join(text_parts)
                
                # If it's just a simple structure with 'content' field
                if 'content' in parsed_content:
                    return parsed_content['content']
                
                # If none of the above, return the JSON as string
                return content_data
            else:
                # If parsed JSON is not a dict, return original string
                return content_data
        except json.JSONDecodeError:
            # If it's not JSON, return as is
            return content_data
    else:
        # If it's already not a string, convert to string
        return str(content_data)

def generate_graph_data(content):
    """Generate hierarchical graph data from content using AI"""
    try:
        logging.info(f"Generating graph data for content: {content.get('title', 'Unknown')}")
        
        # Use AI service to generate detailed hierarchical structure
        hierarchy_data = ai_service.generate_hierarchical_graph_structure(content['content'])
        
        if 'error' in hierarchy_data:
            logging.warning(f"AI service returned error: {hierarchy_data['error']}")
            # Fallback to legacy method
            return generate_legacy_graph_data(content)
        
        logging.info("Successfully received hierarchy data from AI service")
        
        # Convert AI hierarchy to graph format
        nodes = []
        links = []
        node_counter = 0
        
        # Main topic node
        main_topic = hierarchy_data.get('main_topic', {})
        main_node = {
            'id': str(node_counter),
            'name': main_topic.get('title', content.get('title', 'Main Topic')),
            'type': 'main_topic',
            'level': 0,
            'size': 50,
            'content': main_topic.get('description', 'Central concept'),
            'complexity': main_topic.get('complexity_level', 'intermediate'),
            'color': '#1e3a8a'
        }
        nodes.append(main_node)
        node_counter += 1
        
        # Process hierarchy levels
        level_colors = {
            1: '#3b82f6',  # Blue
            2: '#10b981',  # Green
            3: '#f59e0b',  # Yellow
            4: '#ef4444',  # Red
            5: '#8b5cf6'   # Purple
        }
        
        node_id_map = {'main': '0'}  # Map node titles to IDs
        
        for level_data in hierarchy_data.get('hierarchy_levels', []):
            level_num = level_data.get('level', 1)
            level_title = level_data.get('title', f'Level {level_num}')
            
            # Process nodes in this level directly (no level header)
            for node_data in level_data.get('nodes', []):
                node_id = str(node_counter)
                node_title = node_data.get('title', f'Node {node_counter}')
                
                # Determine node size based on importance
                importance = node_data.get('importance', 'medium')
                size_map = {'high': 35, 'medium': 28, 'low': 22}
                node_size = size_map.get(importance, 28)
                
                # Determine node type color
                node_type = node_data.get('type', 'concept')
                type_colors = {
                    'concept': '#3b82f6',
                    'definition': '#10b981',
                    'principle': '#f59e0b',
                    'example': '#ef4444',
                    'application': '#8b5cf6'
                }
                
                concept_node = {
                    'id': node_id,
                    'name': node_title,
                    'type': node_type,
                    'level': level_num,
                    'size': node_size,
                    'content': node_data.get('description', ''),
                    'importance': importance,
                    'prerequisites': node_data.get('prerequisites', []),
                    'examples': node_data.get('examples', []),
                    'applications': node_data.get('applications', []),
                    'color': type_colors.get(node_type, level_colors.get(level_num, '#6b7280'))
                }
                nodes.append(concept_node)
                
                # Store node mapping
                node_id_map[node_data.get('id', node_title.lower())] = node_id
                
                # Link to main topic (level 1) or previous level
                if level_num == 1:
                    links.append({
                        'source': '0',
                        'target': node_id,
                        'value': 3,
                        'type': 'hierarchy'
                    })
                
                node_counter += 1
        
        # Add relationships from AI analysis
        for relationship in hierarchy_data.get('relationships', []):
            source_id = node_id_map.get(relationship.get('source', ''))
            target_id = node_id_map.get(relationship.get('target', ''))
            
            if source_id and target_id and source_id != target_id:
                rel_type = relationship.get('relationship_type', 'related')
                strength = relationship.get('strength', 'medium')
                
                strength_values = {'strong': 3, 'medium': 2, 'weak': 1}
                link_value = strength_values.get(strength, 2)
                
                links.append({
                    'source': source_id,
                    'target': target_id,
                    'value': link_value,
                    'type': rel_type,
                    'description': relationship.get('description', '')
                })
        
        # Add learning path information
        learning_path = hierarchy_data.get('learning_path', [])
        difficulty_progression = hierarchy_data.get('difficulty_progression', {})
        
        # Ensure we have at least a basic structure
        if len(nodes) == 1:  # Only main topic
            # Add some basic nodes
            basic_nodes = [
                {
                    'id': '1',
                    'name': 'Key Concept 1',
                    'type': 'concept',
                    'level': 1,
                    'size': 30,
                    'content': 'Primary concept from the content',
                    'color': '#3b82f6'
                },
                {
                    'id': '2',
                    'name': 'Key Concept 2',
                    'type': 'definition',
                    'level': 1,
                    'size': 28,
                    'content': 'Secondary concept from the content',
                    'color': '#10b981'
                }
            ]
            nodes.extend(basic_nodes)
            
            # Add basic links
            links.extend([
                {'source': '0', 'target': '1', 'value': 3, 'type': 'hierarchy'},
                {'source': '0', 'target': '2', 'value': 3, 'type': 'hierarchy'},
                {'source': '1', 'target': '2', 'value': 2, 'type': 'related'}
            ])
        
        return {
            'nodes': nodes,
            'links': links,
            'learning_path': learning_path,
            'difficulty_progression': difficulty_progression,
            'metadata': {
                'total_levels': len(hierarchy_data.get('hierarchy_levels', [])),
                'total_concepts': len(nodes),
                'complexity': main_topic.get('complexity_level', 'intermediate')
            }
        }
        
    except Exception as e:
        logging.error(f"Error generating AI-powered graph: {e}")
        # Fallback to legacy method
        return generate_legacy_graph_data(content)

def generate_legacy_graph_data(content):
    """Generate hierarchical graph data from content"""
    try:
        # Parse content data
        content_data = content['content']
        
        if isinstance(content_data, str):
            try:
                structured_data = json.loads(content_data)
            except json.JSONDecodeError:
                # Create simple graph from text content
                return create_simple_graph_from_text(content_data, content.get('title', 'Content'))
        else:
            structured_data = content_data
        
        # Extract nodes and links from structured data
        nodes = []
        links = []
        node_id = 0
        
        # Main title node
        title_node = {
            'id': str(node_id),
            'name': structured_data.get('title', content.get('title', 'Content')),
            'type': 'main_topic',
            'level': 0,
            'size': 40,
            'content': structured_data.get('executive_summary', 'Main content')
        }
        nodes.append(title_node)
        node_id += 1
        
        # Process main sections
        if structured_data.get('main_sections'):
            for i, section in enumerate(structured_data['main_sections']):
                section_node = {
                    'id': str(node_id),
                    'name': section.get('section_title', f'Section {i+1}'),
                    'type': 'sub_topic',
                    'level': 1,
                    'size': 30,
                    'content': section.get('content', '')[:200] + '...' if len(section.get('content', '')) > 200 else section.get('content', ''),
                    'children': []
                }
                nodes.append(section_node)
                
                # Link to main title
                links.append({
                    'source': '0',
                    'target': str(node_id),
                    'value': 3
                })
                
                section_id = node_id
                node_id += 1
                
                # Process key points within sections
                if section.get('key_points'):
                    for j, point in enumerate(section['key_points']):
                        point_node = {
                            'id': str(node_id),
                            'name': point[:30] + '...' if len(point) > 30 else point,
                            'type': 'key_point',
                            'level': 2,
                            'size': 20,
                            'content': point
                        }
                        nodes.append(point_node)
                        section_node['children'].append(point)
                        
                        # Link to section
                        links.append({
                            'source': str(section_id),
                            'target': str(node_id),
                            'value': 2
                        })
                        node_id += 1
        
        # Process concepts glossary
        if structured_data.get('concepts_glossary'):
            concepts_main_node = {
                'id': str(node_id),
                'name': 'Key Concepts',
                'type': 'sub_topic',
                'level': 1,
                'size': 30,
                'content': 'Important concepts and definitions'
            }
            nodes.append(concepts_main_node)
            
            # Link to main title
            links.append({
                'source': '0',
                'target': str(node_id),
                'value': 3
            })
            
            concepts_main_id = node_id
            node_id += 1
            
            for concept, definition in structured_data['concepts_glossary'].items():
                concept_node = {
                    'id': str(node_id),
                    'name': concept,
                    'type': 'concept',
                    'level': 2,
                    'size': 25,
                    'content': definition
                }
                nodes.append(concept_node)
                
                # Link to concepts main node
                links.append({
                    'source': str(concepts_main_id),
                    'target': str(node_id),
                    'value': 2
                })
                node_id += 1
        
        # Process key takeaways
        if structured_data.get('key_takeaways'):
            takeaways_node = {
                'id': str(node_id),
                'name': 'Key Takeaways',
                'type': 'sub_topic',
                'level': 1,
                'size': 30,
                'content': 'Main lessons and insights'
            }
            nodes.append(takeaways_node)
            
            # Link to main title
            links.append({
                'source': '0',
                'target': str(node_id),
                'value': 3
            })
            
            takeaways_id = node_id
            node_id += 1
            
            for takeaway in structured_data['key_takeaways']:
                takeaway_node = {
                    'id': str(node_id),
                    'name': takeaway[:30] + '...' if len(takeaway) > 30 else takeaway,
                    'type': 'key_point',
                    'level': 2,
                    'size': 20,
                    'content': takeaway
                }
                nodes.append(takeaway_node)
                
                # Link to takeaways node
                links.append({
                    'source': str(takeaways_id),
                    'target': str(node_id),
                    'value': 2
                })
                node_id += 1
        
        return {
            'nodes': nodes,
            'links': links
        }
        
    except Exception as e:
        # Fallback to simple graph
        return create_simple_graph_from_text(extract_text_from_content(content['content']), content.get('title', 'Content'))

def create_simple_graph_from_text(text, title):
    """Create a simple graph structure from plain text"""
    # Split text into paragraphs and create basic hierarchy
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    nodes = []
    links = []
    
    # Main title node
    nodes.append({
        'id': '0',
        'name': title,
        'type': 'main_topic',
        'level': 0,
        'size': 40,
        'content': text[:200] + '...' if len(text) > 200 else text
    })
    
    # Create nodes for each paragraph/section
    for i, paragraph in enumerate(paragraphs[:10]):  # Limit to first 10 paragraphs
        node_name = paragraph[:50] + '...' if len(paragraph) > 50 else paragraph
        nodes.append({
            'id': str(i + 1),
            'name': node_name,
            'type': 'sub_topic' if i < 5 else 'key_point',
            'level': 1,
            'size': 25 if i < 5 else 20,
            'content': paragraph
        })
        
        # Link to main node
        links.append({
            'source': '0',
            'target': str(i + 1),
            'value': 2
        })
    
    return {
        'nodes': nodes,
        'links': links
    }

# Upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Login required decorator for frontend
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('frontend_login'))
        return f(*args, **kwargs)
    return decorated_function

# Frontend Routes
@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def frontend_login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        user = db.get_user(username)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def frontend_signup():
    """Signup page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
        
        if db.get_user(username):
            flash('Username already exists', 'error')
            return render_template('signup.html')
        
        hashed_password = generate_password_hash(password)
        user_id = db.create_user(username, hashed_password)
        
        if user_id:
            session['user_id'] = str(user_id)
            session['username'] = username
            flash('Account created successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Error creating account', 'error')
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with upload form"""
    return render_template('dashboard.html')

@app.route('/upload', methods=['POST'])
@login_required
def frontend_upload():
    """Handle file upload from frontend"""
    try:
        content_type = None
        file = request.files.get('file')
        text_content = request.form.get('text_content')
        
        if not file and not text_content:
            flash('Please select a file or enter text content', 'error')
            return redirect(url_for('dashboard'))
        
        if text_content:
            content_type = 'text'
            # Process text content
            processed_content = content_processor.process_text(text_content)
        elif file:
            filename = secure_filename(file.filename)
            if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv')):
                content_type = 'video'
            elif filename.lower().endswith('.pdf'):
                content_type = 'pdf'
            else:
                flash('Unsupported file type', 'error')
                return redirect(url_for('dashboard'))
            
            # Validate file
            validation_result = validate_upload(file, content_type)
            if not validation_result['valid']:
                flash(validation_result['error'], 'error')
                return redirect(url_for('dashboard'))
            
            # Save and process file
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Process content based on type
            if content_type == 'video':
                processed_content = content_processor.process_video(file_path)
            else:  # pdf
                processed_content = content_processor.process_pdf(file_path)
            
            # Clean up uploaded file after processing
            os.remove(file_path)
        
        # Generate structured content using AI
        structured_content = ai_service.generate_structured_content(
            processed_content['text'], 
            content_type=content_type
        )
        
        # Generate title from structured content or use fallback
        if isinstance(structured_content, dict) and 'title' in structured_content:
            title = structured_content['title']
        else:
            title = ai_service.generate_title(processed_content['text'])
        
        # Combine metadata
        final_metadata = processed_content.get('metadata', {})
        if isinstance(structured_content, dict) and 'metadata' in structured_content:
            final_metadata.update(structured_content['metadata'])
        
        # Store in database with structured content
        content_to_store = structured_content if isinstance(structured_content, dict) and 'error' not in structured_content else processed_content['text']
        
        content_id = db.store_content(
            user_id=session['user_id'],
            title=title,
            content=json.dumps(content_to_store) if isinstance(content_to_store, dict) else content_to_store,
            content_type=content_type,
            metadata=final_metadata
        )
        
        # Redirect to processing page
        return redirect(url_for('processing', content_id=content_id))
        
    except Exception as e:
        flash(f'Error uploading content: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/processing/<content_id>')
@login_required
def processing(content_id):
    """Processing page with loading screen"""
    return render_template('processing.html', content_id=content_id)

@app.route('/options/<content_id>')
@login_required
def content_options(content_id):
    """Page with summary, notes, quiz options"""
    # Verify user owns this content
    content = db.get_content(content_id, session['user_id'])
    if not content:
        flash('Content not found', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('content_options.html', content_id=content_id, content=content)

@app.route('/structured/<content_id>')
@login_required
def view_structured_content(content_id):
    """View structured content page"""
    content = db.get_content(content_id, session['user_id'])
    if not content:
        flash('Content not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Try to parse structured content
    try:
        content_data = content['content']
        if isinstance(content_data, str):
            try:
                structured_data = json.loads(content_data)
            except json.JSONDecodeError:
                # If it's not JSON, create a basic structure
                structured_data = {
                    "title": content['title'],
                    "executive_summary": content_data[:300] + "..." if len(content_data) > 300 else content_data,
                    "main_sections": [
                        {
                            "section_title": "Content",
                            "content": content_data,
                            "key_points": []
                        }
                    ],
                    "content_type": content.get('content_type', 'text')
                }
        else:
            structured_data = content_data
            
        return render_template('structured_content.html', content=content, structured_data=structured_data)
    except Exception as e:
        flash(f'Error loading structured content: {str(e)}', 'error')
        return redirect(url_for('content_options', content_id=content_id))

@app.route('/graph/<content_id>')
@login_required
def view_graph_content(content_id):
    """View interactive graph content page"""
    content = db.get_content(content_id, session['user_id'])
    if not content:
        flash('Content not found', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('graph_content.html', content=content)

@app.route('/api/graph-data/<content_id>')
@login_required
def get_graph_data(content_id):
    """API endpoint to get graph data for content"""
    try:
        content = db.get_content(content_id, session['user_id'])
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        # Generate graph data from content
        graph_data = generate_graph_data(content)
        return jsonify(graph_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/summary/<content_id>')
@login_required
def frontend_summary(content_id):
    """Summary page"""
    content = db.get_content(content_id, session['user_id'])
    if not content:
        flash('Content not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Generate summary using AI service
    try:
        # Extract text from structured content
        content_text = extract_text_from_content(content['content'])
        summary_data = ai_service.generate_summary(content_text, 'english')
        return render_template('summary.html', content=content, summary=summary_data)
    except Exception as e:
        flash(f'Error generating summary: {str(e)}', 'error')
        return redirect(url_for('content_options', content_id=content_id))

@app.route('/notes/<content_id>')
@login_required
def frontend_notes(content_id):
    """Notes page"""
    content = db.get_content(content_id, session['user_id'])
    if not content:
        flash('Content not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Generate notes using AI service
    try:
        # Extract text from structured content
        content_text = extract_text_from_content(content['content'])
        notes_data = ai_service.generate_notes(content_text, 'english')
        return render_template('notes.html', content=content, notes=notes_data)
    except Exception as e:
        flash(f'Error generating notes: {str(e)}', 'error')
        return redirect(url_for('content_options', content_id=content_id))

@app.route('/quiz/<content_id>')
@login_required
def frontend_quiz(content_id):
    """Quiz page"""
    num_questions = request.args.get('num_questions', 5, type=int)
    
    content = db.get_content(content_id, session['user_id'])
    if not content:
        flash('Content not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Generate quiz using AI service
    try:
        # Extract text from structured content
        content_text = extract_text_from_content(content['content'])
        quiz_data = ai_service.generate_quiz(content_text, 'english', num_questions)
        return render_template('quiz.html', content=content, quiz=quiz_data)
    except Exception as e:
        flash(f'Error generating quiz: {str(e)}', 'error')
        return redirect(url_for('content_options', content_id=content_id))

@app.route('/my-content')
@login_required
def my_content():
    """Page showing all user's content"""
    try:
        user_content = db.get_user_contents(session['user_id'])
        return render_template('my_content.html', content_list=user_content)
    except Exception as e:
        flash(f'Error loading content: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/delete-content/<content_id>', methods=['POST'])
@login_required
def delete_content(content_id):
    """Delete content"""
    try:
        # Verify user owns this content before deleting
        content = db.get_content(content_id, session['user_id'])
        if not content:
            flash('Content not found or you do not have permission to delete it', 'error')
            return redirect(url_for('my_content'))
        
        # Delete the content
        if db.delete_content(content_id, session['user_id']):
            flash(f'Content "{content["title"]}" has been deleted successfully', 'success')
        else:
            flash('Failed to delete content', 'error')
        
    except Exception as e:
        flash(f'Error deleting content: {str(e)}', 'error')
    
    return redirect(url_for('my_content'))

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Check if user already exists
        if db.get_user(username):
            return jsonify({'error': 'Username already exists'}), 409
        
        # Create new user
        hashed_password = generate_password_hash(password)
        user_id = db.create_user(username, hashed_password)
        
        return jsonify({
            'message': 'User created successfully',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """Authenticate user and return JWT token"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = db.get_user(username)
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        access_token = create_access_token(
            identity=str(user['_id']),
            expires_delta=timedelta(hours=24)
        )
        
        return jsonify({
            'access_token': access_token,
            'user_id': str(user['_id'])
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_content():
    """Upload and process content (video, PDF, or text)"""
    try:
        user_id = get_jwt_identity()
        
        # Get content type and data
        content_type = request.form.get('type')  # 'video', 'pdf', 'text'
        
        if content_type not in ['video', 'pdf', 'text']:
            return jsonify({'error': 'Invalid content type. Must be video, pdf, or text'}), 400
        
        # Validate and process based on content type
        if content_type == 'text':
            content_text = request.form.get('content')
            if not content_text:
                return jsonify({'error': 'Content text is required'}), 400
            
            processed_content = content_processor.process_text(content_text)
            
        elif content_type in ['video', 'pdf']:
            if 'file' not in request.files:
                return jsonify({'error': 'File is required'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Validate file
            validation_result = validate_upload(file, content_type)
            if not validation_result['valid']:
                return jsonify({'error': validation_result['error']}), 400
            
            # Save file
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Process content based on type
            if content_type == 'video':
                processed_content = content_processor.process_video(file_path)
            else:  # pdf
                processed_content = content_processor.process_pdf(file_path)
            
            # Clean up uploaded file after processing
            os.remove(file_path)
        
        # Generate structured content using AI
        structured_content = ai_service.generate_structured_content(
            processed_content['text'], 
            content_type=content_type
        )
        
        # Generate title from structured content or use fallback
        if isinstance(structured_content, dict) and 'title' in structured_content:
            title = structured_content['title']
        else:
            title = ai_service.generate_title(processed_content['text'])
        
        # Combine metadata
        final_metadata = processed_content.get('metadata', {})
        if isinstance(structured_content, dict) and 'metadata' in structured_content:
            final_metadata.update(structured_content['metadata'])
        
        # Store in database with structured content
        content_to_store = structured_content if isinstance(structured_content, dict) and 'error' not in structured_content else processed_content['text']
        
        # Store in database
        content_id = db.store_content(
            user_id=user_id,
            title=title,
            content=json.dumps(content_to_store) if isinstance(content_to_store, dict) else content_to_store,
            content_type=content_type,
            metadata=final_metadata
        )
        
        return jsonify({
            'message': 'Content uploaded and processed successfully',
            'content_id': content_id,
            'title': title
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list', methods=['GET'])
@jwt_required()
def list_content():
    """Get all content for the authenticated user"""
    try:
        user_id = get_jwt_identity()
        contents = db.get_user_contents(user_id)
        
        return jsonify({
            'contents': contents
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summary', methods=['POST'])
@jwt_required()
def generate_summary():
    """Generate summary of content"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        content_id = data.get('content_id')
        language = data.get('language', 'english')
        
        if not content_id:
            return jsonify({'error': 'Content ID is required'}), 400
        
        # Get content from database
        content = db.get_content(content_id, user_id)
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        # Extract text from structured content
        content_text = extract_text_from_content(content['content'])
        
        # Generate summary using AI
        summary = ai_service.generate_summary(content_text, language)
        
        return jsonify({
            'content_id': content_id,
            'title': content['title'],
            'summary': summary,
            'language': language
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz', methods=['POST'])
@jwt_required()
def generate_quiz():
    """Generate quiz from content"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        content_id = data.get('content_id')
        language = data.get('language', 'english')
        num_questions = data.get('num_questions', None)
        
        if not content_id:
            return jsonify({'error': 'Content ID is required'}), 400
        
        if num_questions and (num_questions < 1 or num_questions > 50):
            return jsonify({'error': 'Number of questions must be between 1 and 50'}), 400
        
        # Get content from database
        content = db.get_content(content_id, user_id)
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        # Extract text from structured content
        content_text = extract_text_from_content(content['content'])
        
        # Generate quiz using AI
        quiz = ai_service.generate_quiz(content_text, language, num_questions)
        
        return jsonify({
            'content_id': content_id,
            'title': content['title'],
            'quiz': quiz,
            'language': language,
            'total_questions': len(quiz['questions'])
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes', methods=['POST'])
@jwt_required()
def generate_notes():
    """Generate structured notes from content"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        content_id = data.get('content_id')
        language = data.get('language', 'english')
        
        if not content_id:
            return jsonify({'error': 'Content ID is required'}), 400
        
        # Get content from database
        content = db.get_content(content_id, user_id)
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        # Extract text from structured content
        content_text = extract_text_from_content(content['content'])
        
        # Generate notes using AI
        notes = ai_service.generate_notes(content_text, language)
        
        return jsonify({
            'content_id': content_id,
            'title': content['title'],
            'notes': notes,
            'language': language
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/content/<content_id>', methods=['GET'])
@jwt_required()
def get_structured_content(content_id):
    """Get structured content details"""
    try:
        user_id = get_jwt_identity()
        
        # Get content from database
        content = db.get_content(content_id, user_id)
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        # Try to parse structured content if it's JSON
        content_data = content['content']
        try:
            if isinstance(content_data, str):
                structured_data = json.loads(content_data)
            else:
                structured_data = content_data
        except (json.JSONDecodeError, TypeError):
            # If it's not structured JSON, create a basic structure
            structured_data = {
                "title": content['title'],
                "content": content_data,
                "content_type": content.get('content_type', 'text'),
                "metadata": content.get('metadata', {})
            }
        
        return jsonify({
            'content_id': content_id,
            'title': content['title'],
            'structured_content': structured_data,
            'content_type': content.get('content_type', 'text'),
            'metadata': content.get('metadata', {}),
            'created_at': content.get('created_at')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/content/<content_id>', methods=['DELETE'])
@jwt_required()
def api_delete_content(content_id):
    """Delete content via API"""
    try:
        user_id = get_jwt_identity()
        
        # Verify user owns this content before deleting
        content = db.get_content(content_id, user_id)
        if not content:
            return jsonify({'error': 'Content not found or you do not have permission to delete it'}), 404
        
        # Delete the content
        if db.delete_content(content_id, user_id):
            return jsonify({
                'message': f'Content "{content["title"]}" has been deleted successfully',
                'content_id': content_id
            }), 200
        else:
            return jsonify({'error': 'Failed to delete content'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# PDF Download Routes
@app.route('/download/summary/<content_id>/pdf')
@login_required
def download_summary_pdf(content_id):
    """Download summary as PDF"""
    try:
        content = db.get_content(content_id, session['user_id'])
        if not content:
            flash('Content not found', 'error')
            return redirect(url_for('dashboard'))
        
        # Generate summary data
        summary_data = ai_service.generate_summary(
            extract_text_from_content(content['content']),
            content.get('title', 'Untitled Content')
        )
        
        if isinstance(summary_data, dict) and 'error' not in summary_data:
            # Generate PDF
            pdf_buffer = pdf_generator.generate_summary_pdf(content, summary_data)
            
            # Return PDF as download
            filename = f"summary_{content.get('title', 'content')}.pdf"
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            flash('Error generating summary PDF', 'error')
            return redirect(url_for('frontend_summary', content_id=content_id))
            
    except Exception as e:
        flash(f'Error downloading PDF: {str(e)}', 'error')
        return redirect(url_for('frontend_summary', content_id=content_id))

@app.route('/download/notes/<content_id>/pdf')
@login_required
def download_notes_pdf(content_id):
    """Download notes as PDF"""
    try:
        content = db.get_content(content_id, session['user_id'])
        if not content:
            flash('Content not found', 'error')
            return redirect(url_for('dashboard'))
        
        # Generate notes data
        notes_data = ai_service.generate_notes(
            extract_text_from_content(content['content']),
            content.get('title', 'Untitled Content')
        )
        
        if isinstance(notes_data, dict) and 'error' not in notes_data:
            # Generate PDF
            pdf_buffer = pdf_generator.generate_notes_pdf(content, notes_data)
            
            # Return PDF as download
            filename = f"notes_{content.get('title', 'content')}.pdf"
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            flash('Error generating notes PDF', 'error')
            return redirect(url_for('frontend_notes', content_id=content_id))
            
    except Exception as e:
        flash(f'Error downloading PDF: {str(e)}', 'error')
        return redirect(url_for('frontend_notes', content_id=content_id))

@app.route('/download/quiz/<content_id>/pdf')
@login_required
def download_quiz_pdf(content_id):
    """Download quiz as PDF"""
    try:
        content = db.get_content(content_id, session['user_id'])
        if not content:
            flash('Content not found', 'error')
            return redirect(url_for('dashboard'))
        
        # Get number of questions from query parameter
        num_questions = request.args.get('num_questions', 10, type=int)
        
        # Generate quiz data
        quiz_data = ai_service.generate_quiz(
            extract_text_from_content(content['content']),
            content.get('title', 'Untitled Content'),
            num_questions=num_questions
        )
        
        if isinstance(quiz_data, dict) and 'error' not in quiz_data:
            # Generate PDF
            pdf_buffer = pdf_generator.generate_quiz_pdf(content, quiz_data)
            
            # Return PDF as download
            filename = f"quiz_{content.get('title', 'content')}.pdf"
            filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
        else:
            flash('Error generating quiz PDF', 'error')
            return redirect(url_for('generate_quiz', content_id=content_id))
            
    except Exception as e:
        flash(f'Error downloading PDF: {str(e)}', 'error')
        return redirect(url_for('generate_quiz', content_id=content_id))

@app.route('/download/report/<content_id>/pdf')
@login_required
def download_report_pdf(content_id):
    """Download comprehensive report as PDF"""
    try:
        content = db.get_content(content_id, session['user_id'])
        if not content:
            flash('Content not found', 'error')
            return redirect(url_for('dashboard'))
        
        content_text = extract_text_from_content(content['content'])
        content_title = content.get('title', 'Untitled Content')
        
        # Generate all data types
        summary_data = ai_service.generate_summary(content_text, content_title)
        notes_data = ai_service.generate_notes(content_text, content_title)
        quiz_data = ai_service.generate_quiz(content_text, content_title, num_questions=5)
        
        # Generate comprehensive PDF
        pdf_buffer = pdf_generator.generate_report_pdf(content, summary_data, notes_data, quiz_data)
        
        # Return PDF as download
        filename = f"report_{content.get('title', 'content')}.pdf"
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        flash(f'Error downloading PDF: {str(e)}', 'error')
        return redirect(url_for('content_options', content_id=content_id))

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'StudySahayak API'}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
