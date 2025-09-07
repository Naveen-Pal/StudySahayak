import google.generativeai as genai
from config import Config
import json
import logging
import requests

class AIService:
    """Service for AI-powered content generation using Gemini API"""
    
    def __init__(self):
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            logging.warning("Gemini API key not configured")
            self.model = None
        
        self.serp_api_key = Config.SERP_API_KEY
    
    def _clean_json_response(self, response_text):
        """Clean AI response to extract valid JSON"""
        import re
        
        # Remove markdown code blocks
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        response_text = response_text.strip()
        
        # Try to find JSON content between braces
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return response_text
    
    def generate_title(self, content):
        """Generate a title for the content"""
        if not self.model:
            return "Untitled Content"
        
        try:
            prompt = f"""
            Based on the following content, generate a concise and descriptive title (maximum 60 characters):
            
            Content: {content[:500]}...
            
            Return only the title, nothing else.
            """
            
            response = self.model.generate_content(prompt)
            title = response.text.strip().replace('"', '').replace("'", "")
            return title[:60] if len(title) > 60 else title
            
        except Exception as e:
            logging.error(f"Error generating title: {e}")
            return "Generated Content"
    
    def generate_structured_content(self, raw_content, content_type="text", language="english"):
        """Generate detailed, well-structured content from raw input"""
        if not self.model:
            return {"error": "AI service not available"}
        
        try:
            # Create a comprehensive prompt based on content type
            type_specific_instruction = {
                "video": "This content is transcribed from a video. Please organize it into a comprehensive educational material.",
                "pdf": "This content is extracted from a PDF document. Please restructure it into a well-organized format.",
                "text": "This is raw text content. Please organize it into a structured educational format."
            }
            
            prompt = f"""
            {type_specific_instruction.get(content_type, "Please organize this content")}
            
            Transform the following content into a detailed, well-structured educational material in {language}. 
            
            Raw Content: {raw_content}
            
            Please create a comprehensive structured document with the following sections:
            
            1. **Executive Summary** - Brief overview of the main topic
            2. **Introduction** - Context and background information
            3. **Main Content** - Detailed breakdown with:
               - Key concepts and definitions
               - Important points organized in logical sections
               - Examples and explanations where applicable
            4. **Key Takeaways** - Important points to remember
            5. **Conclusion** - Summary and final thoughts
            
            Format the response as a JSON object with the following structure:
            {{
                "title": "Comprehensive title for the content",
                "executive_summary": "Brief overview paragraph",
                "introduction": "Introduction paragraph with context",
                "main_sections": [
                    {{
                        "section_title": "Section name",
                        "content": "Detailed content for this section",
                        "key_points": ["Point 1", "Point 2", "Point 3"]
                    }}
                ],
                "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
                "conclusion": "Conclusion paragraph",
                "concepts_glossary": {{"concept": "definition"}},
                "metadata": {{
                    "content_type": "{content_type}",
                    "language": "{language}",
                    "estimated_read_time": "X minutes"
                }}
            }}
            
            Ensure the content is educational, comprehensive, and well-organized.
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                # Clean the response before parsing
                cleaned_response = self._clean_json_response(response.text)
                structured_content = json.loads(cleaned_response)
                return structured_content
            except json.JSONDecodeError:
                # If JSON parsing fails, create a structured format from plain text
                return self._create_fallback_structure(response.text, content_type, language)
            
        except Exception as e:
            logging.error(f"Error generating structured content: {e}")
            return {"error": f"Failed to generate structured content: {str(e)}"}
    
    def _create_fallback_structure(self, text_content, content_type, language):
        """Create a fallback structured format when JSON parsing fails"""
        return {
            "title": "Structured Content",
            "executive_summary": text_content[:200] + "..." if len(text_content) > 200 else text_content,
            "introduction": "This content has been processed and structured for better understanding.",
            "main_sections": [
                {
                    "section_title": "Main Content",
                    "content": text_content,
                    "key_points": ["Content has been processed", "Review the material carefully"]
                }
            ],
            "key_takeaways": ["Important information extracted", "Content organized for learning"],
            "conclusion": "This material provides valuable insights for study and reference.",
            "concepts_glossary": {},
            "metadata": {
                "content_type": content_type,
                "language": language,
                "estimated_read_time": f"{max(1, len(text_content.split()) // 200)} minutes"
            }
        }
    
    def generate_summary(self, content, language="english"):
        """Generate a summary of the content in specified language"""
        if not self.model:
            return {"error": "AI service not available"}
        
        try:
            prompt = f"""
            Create a comprehensive summary of the following content in {language}. 
            The summary should be well-structured with key points and main concepts.
            
            Content: {content}
            
            Please provide the summary in a clear, organized format with:
            1. Main topic/theme
            2. Key points (bullet format)
            3. Important concepts or definitions
            4. Conclusion or takeaways
            
            Return the response in valid JSON format with the following structure:
            {{
                "main_topic": "topic here",
                "key_points": ["point 1", "point 2", ...],
                "concepts": {{"concept": "definition", ...}},
                "conclusion": "conclusion here"
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                # Clean and parse JSON response
                cleaned_response = self._clean_json_response(response.text)
                summary_json = json.loads(cleaned_response)
                return summary_json
            except json.JSONDecodeError:
                # If JSON parsing fails, return as plain text
                return {
                    "main_topic": "Summary",
                    "summary_text": response.text,
                    "language": language
                }
            
        except Exception as e:
            logging.error(f"Error generating summary: {e}")
            return {"error": f"Failed to generate summary: {str(e)}"}
    
    def generate_quiz(self, content, language="english", num_questions=None):
        """Generate a quiz from the content"""
        if not self.model:
            return {"error": "AI service not available"}
        
        try:
            # Determine number of questions based on content length if not specified
            if not num_questions:
                content_length = len(content.split())
                if content_length < 200:
                    num_questions = 5
                elif content_length < 500:
                    num_questions = 10
                elif content_length < 1000:
                    num_questions = 15
                else:
                    num_questions = 20
            
            # Ensure within limits
            num_questions = min(max(num_questions, 1), 50)
            
            prompt = f"""
            Create a quiz with {num_questions} multiple-choice questions based on the following content in {language}.
            
            Content: {content}
            
            Requirements:
            - Each question should have 4 options (A, B, C, D)
            - Only one correct answer per question
            - Questions should cover different aspects of the content
            - Include a mix of difficulty levels
            - Questions should be clear and unambiguous
            
            Return the response in valid JSON format:
            {{
                "quiz_title": "title here",
                "total_questions": {num_questions},
                "questions": [
                    {{
                        "id": 1,
                        "question": "question text",
                        "options": {{
                            "A": "option A",
                            "B": "option B", 
                            "C": "option C",
                            "D": "option D"
                        }},
                        "correct_answer": "A",
                        "explanation": "explanation of correct answer"
                    }}
                ]
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                # Clean and parse JSON response
                cleaned_response = self._clean_json_response(response.text)
                quiz_json = json.loads(cleaned_response)
                return quiz_json
            except json.JSONDecodeError:
                # Fallback format if JSON parsing fails
                return {
                    "quiz_title": "Generated Quiz",
                    "total_questions": 0,
                    "questions": [],
                    "error": "Failed to parse quiz format",
                    "raw_response": response.text
                }
            
        except Exception as e:
            logging.error(f"Error generating quiz: {e}")
            return {"error": f"Failed to generate quiz: {str(e)}"}
    
    def generate_notes(self, content, language="english"):
        """Generate comprehensive, detailed notes from the content"""
        if not self.model:
            return {"error": "AI service not available"}
        
        try:
            prompt = f"""
            Create extremely detailed, comprehensive study notes from the following content in {language}.
            These notes should be MUCH MORE detailed than a summary - they should cover everything important for deep learning and understanding.
            
            Content: {content}
            
            Please create thorough notes with:
            1. Detailed explanations of all concepts (not just bullet points)
            2. Multiple sections covering different aspects
            3. In-depth analysis and context
            4. Examples, analogies, and practical applications where relevant
            5. Step-by-step breakdowns of processes
            6. Important definitions and terminology
            7. Connections between different concepts
            8. Practical implications and real-world applications
            9. Potential questions and areas for further study
            
            Make the notes comprehensive enough that someone could learn the entire topic from these notes alone.
            Each section should have substantial content (multiple paragraphs, not just bullet points).
            
            Return the response in valid JSON format:
            {{
                "title": "comprehensive title for the notes",
                "sections": [
                    {{
                        "heading": "detailed section heading",
                        "content": "extensive section content with detailed explanations, examples, and analysis. Use plain text with newlines for formatting, not markdown.",
                        "key_concepts": ["concept1", "concept2", "concept3"],
                        "subsections": [
                            {{
                                "subheading": "subsection title",
                                "subcontent": "detailed subsection content"
                            }}
                        ]
                    }}
                ],
                "summary": "comprehensive overall summary that ties everything together",
                "key_takeaways": ["detailed takeaway 1", "detailed takeaway 2", "detailed takeaway 3"],
                "study_tips": ["tip for understanding concept 1", "tip for remembering concept 2"],
                "further_reading": ["suggested area 1", "suggested area 2"]
            }}
            
            IMPORTANT: Use plain text with newlines for formatting. Do NOT use markdown syntax like *, **, #, etc. Use actual line breaks and spacing for structure.
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                # Clean and parse JSON response
                cleaned_response = self._clean_json_response(response.text)
                notes_json = json.loads(cleaned_response)
                return notes_json
            except json.JSONDecodeError:
                # Fallback format if JSON parsing fails - clean any markdown
                clean_content = response.text.replace('**', '').replace('*', '').replace('#', '').replace('```', '')
                return {
                    "title": "Generated Notes",
                    "content": clean_content,
                    "language": language
                }
            
        except Exception as e:
            logging.error(f"Error generating notes: {e}")
            return {"error": f"Failed to generate notes: {str(e)}"}
    
    def enhance_content_with_web_search(self, content, search_query):
        """Enhance content with web search results using SerpAPI"""
        if not self.serp_api_key:
            logging.warning("SerpAPI key not configured")
            return content
        
        try:
            # Search for additional information using SerpAPI
            search_url = "https://serpapi.com/search"
            params = {
                "engine": "google",
                "q": search_query,
                "api_key": self.serp_api_key,
                "num": 5  # Get top 5 results
            }
            
            response = requests.get(search_url, params=params)
            
            if response.status_code == 200:
                search_results = response.json()
                
                # Extract relevant information from search results
                additional_info = []
                if 'organic_results' in search_results:
                    for result in search_results['organic_results'][:3]:  # Top 3 results
                        if 'snippet' in result:
                            additional_info.append(result['snippet'])
                
                if additional_info:
                    # Use Gemini to integrate search results with original content
                    enhanced_content = self._integrate_search_results(content, additional_info)
                    return enhanced_content
            
            return content
            
        except Exception as e:
            logging.error(f"Error enhancing content with web search: {e}")
            return content
    
    def _integrate_search_results(self, original_content, search_results):
        """Use Gemini to integrate search results with original content"""
        if not self.model:
            return original_content
        
        try:
            search_info = "\n".join(search_results)
            
            prompt = f"""
            Original content:
            {original_content}
            
            Additional information from web search:
            {search_info}
            
            Please enhance the original content by integrating relevant information from the web search results. 
            Keep the original structure and tone, but add valuable insights, recent developments, or additional context where appropriate.
            Ensure the enhanced content flows naturally and maintains accuracy.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logging.error(f"Error integrating search results: {e}")
            return original_content

    def generate_hierarchical_graph_structure(self, content, language="english"):
        """Generate a detailed hierarchical structure for graph visualization"""
        if not self.model:
            logging.warning("AI model not available, using fallback")
            return self._create_enhanced_fallback_hierarchy(content)

        try:
            # Extract text content
            if isinstance(content, dict):
                # Try to get structured content first
                if 'main_sections' in content:
                    text_content = self._extract_from_structured_content(content)
                else:
                    text_content = json.dumps(content)[:2000]  # Limit text size
            else:
                text_content = str(content)[:2000]  # Limit text size

            # Simplified prompt for better reliability
            prompt = f"""
            Create a hierarchical structure for the following content. Return ONLY valid JSON:
            
            Content: {text_content[:1000]}
            
            {{
                "main_topic": {{
                    "title": "Main Topic",
                    "description": "Brief description"
                }},
                "hierarchy_levels": [
                    {{
                        "level": 1,
                        "title": "Key Concepts",
                        "nodes": [
                            {{
                                "id": "concept_1",
                                "title": "First concept",
                                "description": "Description",
                                "type": "concept",
                                "importance": "high"
                            }},
                            {{
                                "id": "concept_2", 
                                "title": "Second concept",
                                "description": "Description",
                                "type": "concept",
                                "importance": "medium"
                            }}
                        ]
                    }}
                ],
                "relationships": [
                    {{
                        "source": "concept_1",
                        "target": "concept_2",
                        "relationship_type": "related",
                        "strength": "medium"
                    }}
                ]
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                cleaned_response = self._clean_json_response(response.text)
                hierarchy_data = json.loads(cleaned_response)
                
                # Validate and enhance the response
                if not hierarchy_data.get('hierarchy_levels'):
                    return self._create_enhanced_fallback_hierarchy(content)
                    
                return hierarchy_data
                
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {e}")
                return self._create_enhanced_fallback_hierarchy(content)
                
        except Exception as e:
            logging.error(f"Error generating hierarchical structure: {e}")
            return self._create_enhanced_fallback_hierarchy(content)

    def _create_enhanced_fallback_hierarchy(self, content):
        """Create an enhanced fallback hierarchical structure"""
        try:
            # Extract text content
            if isinstance(content, dict):
                text_content = self._extract_from_structured_content(content)
            else:
                text_content = str(content)
            
            # Split into concepts
            sentences = [s.strip() for s in text_content.split('.') if s.strip() and len(s.strip()) > 20]
            paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
            
            # Create a more structured hierarchy
            main_concepts = sentences[:4] if len(sentences) >= 4 else paragraphs[:4]
            sub_concepts = sentences[4:8] if len(sentences) >= 8 else paragraphs[4:8] if len(paragraphs) >= 8 else []
            
            hierarchy_levels = []
            
            # Level 1: Main Concepts
            if main_concepts:
                level_1_nodes = []
                for i, concept in enumerate(main_concepts):
                    level_1_nodes.append({
                        "id": f"main_{i}",
                        "title": concept[:60] + "..." if len(concept) > 60 else concept,
                        "description": concept,
                        "type": "concept",
                        "importance": "high" if i < 2 else "medium"
                    })
                
                hierarchy_levels.append({
                    "level": 1,
                    "title": "Main Concepts",
                    "nodes": level_1_nodes
                })
            
            # Level 2: Sub Concepts
            if sub_concepts:
                level_2_nodes = []
                for i, concept in enumerate(sub_concepts):
                    level_2_nodes.append({
                        "id": f"sub_{i}",
                        "title": concept[:50] + "..." if len(concept) > 50 else concept,
                        "description": concept,
                        "type": "definition",
                        "importance": "medium"
                    })
                
                hierarchy_levels.append({
                    "level": 2,
                    "title": "Supporting Details",
                    "nodes": level_2_nodes
                })
            
            # Create relationships
            relationships = []
            if len(hierarchy_levels) >= 2:
                # Connect main concepts to sub concepts
                for i in range(min(len(main_concepts), len(sub_concepts))):
                    relationships.append({
                        "source": f"main_{i}",
                        "target": f"sub_{i}",
                        "relationship_type": "related",
                        "strength": "medium"
                    })
            
            return {
                "main_topic": {
                    "title": "Content Analysis",
                    "description": "Structured breakdown of the content"
                },
                "hierarchy_levels": hierarchy_levels,
                "relationships": relationships,
                "learning_path": [
                    {
                        "step": 1,
                        "focus": "main_0" if main_concepts else "concept_0",
                        "description": "Start with the fundamental concepts"
                    }
                ] if main_concepts else [],
                "difficulty_progression": {
                    "beginner_nodes": [f"main_{i}" for i in range(min(2, len(main_concepts)))],
                    "intermediate_nodes": [f"main_{i}" for i in range(2, len(main_concepts))] + [f"sub_{i}" for i in range(min(2, len(sub_concepts)))],
                    "advanced_nodes": [f"sub_{i}" for i in range(2, len(sub_concepts))]
                }
            }
            
        except Exception as e:
            logging.error(f"Error creating fallback hierarchy: {e}")
            return {
                "main_topic": {
                    "title": "Content",
                    "description": "Basic content structure"
                },
                "hierarchy_levels": [
                    {
                        "level": 1,
                        "title": "Main Topic",
                        "nodes": [
                            {
                                "id": "main_topic",
                                "title": "Main Content",
                                "description": "Primary content area",
                                "type": "concept",
                                "importance": "high"
                            }
                        ]
                    }
                ],
                "relationships": [],
                "learning_path": [],
                "difficulty_progression": {
                    "beginner_nodes": ["main_topic"],
                    "intermediate_nodes": [],
                    "advanced_nodes": []
                }
            }

    def _extract_from_structured_content(self, structured_content):
        """Extract text from structured content"""
        text_parts = []
        
        if isinstance(structured_content, str):
            try:
                structured_content = json.loads(structured_content)
            except:
                return structured_content
        
        # Extract from different parts of structured content
        if structured_content.get('title'):
            text_parts.append(structured_content['title'])
        
        if structured_content.get('executive_summary'):
            text_parts.append(structured_content['executive_summary'])
        
        if structured_content.get('main_sections'):
            for section in structured_content['main_sections']:
                if section.get('section_title'):
                    text_parts.append(section['section_title'])
                if section.get('content'):
                    text_parts.append(section['content'])
                if section.get('key_points'):
                    text_parts.extend(section['key_points'])
        
        if structured_content.get('key_takeaways'):
            text_parts.extend(structured_content['key_takeaways'])
        
        return ' '.join(text_parts)

    def _create_fallback_hierarchy(self, content):
        """Create a fallback hierarchical structure"""
        # Extract key sentences/concepts
        sentences = [s.strip() for s in content.split('.') if s.strip() and len(s.strip()) > 20]
        
        return {
            "main_topic": {
                "title": "Content Analysis",
                "description": "Structured breakdown of the provided content",
                "complexity_level": "intermediate"
            },
            "hierarchy_levels": [
                {
                    "level": 1,
                    "title": "Main Concepts",
                    "nodes": [
                        {
                            "id": f"concept_{i}",
                            "title": sentence[:50] + "..." if len(sentence) > 50 else sentence,
                            "description": sentence,
                            "type": "concept",
                            "importance": "high" if i < 3 else "medium",
                            "prerequisites": [],
                            "related_concepts": [],
                            "examples": [],
                            "applications": []
                        } for i, sentence in enumerate(sentences[:6])
                    ]
                }
            ],
            "relationships": [],
            "learning_path": [
                {
                    "step": 1,
                    "focus": "concept_0",
                    "description": "Start with the fundamental concepts"
                }
            ],
            "difficulty_progression": {
                "beginner_nodes": [f"concept_{i}" for i in range(min(2, len(sentences)))],
                "intermediate_nodes": [f"concept_{i}" for i in range(2, min(4, len(sentences)))],
                "advanced_nodes": [f"concept_{i}" for i in range(4, min(6, len(sentences)))]
            }
        }
