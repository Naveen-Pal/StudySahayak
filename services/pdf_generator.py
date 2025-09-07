from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import Color, black, blue, green, red, orange
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from io import BytesIO
import json
from datetime import datetime

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom styles for different content types"""
        styles = {}
        
        # Title style
        styles['title'] = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=blue
        )
        
        # Subtitle style
        styles['subtitle'] = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            textColor=Color(0.2, 0.4, 0.6)
        )
        
        # Section heading style
        styles['section'] = ParagraphStyle(
            'CustomSection',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=Color(0.1, 0.3, 0.5)
        )
        
        # Body text style
        styles['body'] = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leftIndent=0,
            rightIndent=0
        )
        
        # List item style
        styles['list_item'] = ParagraphStyle(
            'CustomListItem',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20,
            bulletIndent=10
        )
        
        # Quote style
        styles['quote'] = ParagraphStyle(
            'CustomQuote',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            leftIndent=30,
            rightIndent=30,
            textColor=Color(0.3, 0.3, 0.3),
            borderColor=Color(0.8, 0.8, 0.8),
            borderWidth=1,
            borderPadding=10
        )
        
        return styles
    
    def generate_summary_pdf(self, content, summary_data):
        """Generate PDF for summary"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Build story
        story = []
        
        # Title
        story.append(Paragraph("Content Summary", self.custom_styles['title']))
        story.append(Spacer(1, 20))
        
        # Content title
        if content.get('title'):
            story.append(Paragraph(f"<b>Source:</b> {content['title']}", self.custom_styles['subtitle']))
            story.append(Spacer(1, 15))
        
        # Generation date
        story.append(Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                             self.custom_styles['body']))
        story.append(Spacer(1, 20))
        
        # Main topic
        if summary_data.get('main_topic'):
            story.append(Paragraph("Main Topic", self.custom_styles['section']))
            story.append(Paragraph(summary_data['main_topic'], self.custom_styles['body']))
            story.append(Spacer(1, 15))
        
        # Key points
        if summary_data.get('key_points'):
            story.append(Paragraph("Key Points", self.custom_styles['section']))
            for point in summary_data['key_points']:
                story.append(Paragraph(f"• {point}", self.custom_styles['list_item']))
            story.append(Spacer(1, 15))
        
        # Important concepts
        if summary_data.get('concepts'):
            story.append(Paragraph("Important Concepts", self.custom_styles['section']))
            for concept, definition in summary_data['concepts'].items():
                story.append(Paragraph(f"<b>{concept}:</b> {definition}", self.custom_styles['body']))
                story.append(Spacer(1, 8))
            story.append(Spacer(1, 15))
        
        # Conclusion
        if summary_data.get('conclusion'):
            story.append(Paragraph("Conclusion", self.custom_styles['section']))
            story.append(Paragraph(summary_data['conclusion'], self.custom_styles['body']))
            story.append(Spacer(1, 15))
        
        # Summary text (if available)
        if summary_data.get('summary_text'):
            story.append(Paragraph("Summary", self.custom_styles['section']))
            story.append(Paragraph(summary_data['summary_text'], self.custom_styles['body']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_notes_pdf(self, content, notes_data):
        """Generate PDF for notes"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Build story
        story = []
        
        # Title
        story.append(Paragraph("Study Notes", self.custom_styles['title']))
        story.append(Spacer(1, 20))
        
        # Content title
        if notes_data.get('title'):
            story.append(Paragraph(notes_data['title'], self.custom_styles['subtitle']))
            story.append(Spacer(1, 15))
        elif content.get('title'):
            story.append(Paragraph(f"Notes for: {content['title']}", self.custom_styles['subtitle']))
            story.append(Spacer(1, 15))
        
        # Generation date
        story.append(Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                             self.custom_styles['body']))
        story.append(Spacer(1, 20))
        
        # Sections
        if notes_data.get('sections'):
            for section in notes_data['sections']:
                # Section heading
                story.append(Paragraph(section.get('heading', 'Section'), self.custom_styles['section']))
                
                # Section content
                if section.get('content'):
                    story.append(Paragraph(section['content'], self.custom_styles['body']))
                    story.append(Spacer(1, 10))
                
                # Subsections
                if section.get('subsections'):
                    for subsection in section['subsections']:
                        story.append(Paragraph(f"<b>{subsection.get('heading', 'Subsection')}:</b>", 
                                             self.custom_styles['body']))
                        if subsection.get('content'):
                            story.append(Paragraph(subsection['content'], self.custom_styles['body']))
                        story.append(Spacer(1, 8))
                
                # Key points for this section
                if section.get('key_points'):
                    story.append(Paragraph("<b>Key Points:</b>", self.custom_styles['body']))
                    for point in section['key_points']:
                        story.append(Paragraph(f"• {point}", self.custom_styles['list_item']))
                    story.append(Spacer(1, 10))
                
                story.append(Spacer(1, 15))
        
        # Key takeaways
        if notes_data.get('key_takeaways'):
            story.append(Paragraph("Key Takeaways", self.custom_styles['section']))
            for takeaway in notes_data['key_takeaways']:
                story.append(Paragraph(f"• {takeaway}", self.custom_styles['list_item']))
            story.append(Spacer(1, 15))
        
        # Study tips
        if notes_data.get('study_tips'):
            story.append(Paragraph("Study Tips", self.custom_styles['section']))
            for tip in notes_data['study_tips']:
                story.append(Paragraph(f"• {tip}", self.custom_styles['list_item']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_quiz_pdf(self, content, quiz_data, user_answers=None):
        """Generate PDF for quiz"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Build story
        story = []
        
        # Title
        story.append(Paragraph("Quiz", self.custom_styles['title']))
        story.append(Spacer(1, 20))
        
        # Content title
        if content.get('title'):
            story.append(Paragraph(f"Quiz for: {content['title']}", self.custom_styles['subtitle']))
            story.append(Spacer(1, 15))
        
        # Generation date
        story.append(Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                             self.custom_styles['body']))
        story.append(Spacer(1, 20))
        
        # Instructions
        story.append(Paragraph("Instructions", self.custom_styles['section']))
        story.append(Paragraph("Choose the best answer for each question. Mark your answers clearly.", 
                             self.custom_styles['body']))
        story.append(Spacer(1, 20))
        
        # Questions
        if quiz_data.get('questions'):
            for i, question in enumerate(quiz_data['questions'], 1):
                # Question number and text
                story.append(Paragraph(f"<b>Question {i}:</b> {question.get('question', '')}", 
                                     self.custom_styles['body']))
                story.append(Spacer(1, 10))
                
                # Options
                if question.get('options'):
                    for option_key, option_text in question['options'].items():
                        # Highlight correct answer if user_answers provided
                        style = self.custom_styles['list_item']
                        prefix = f"{option_key}. "
                        
                        if user_answers and i-1 < len(user_answers):
                            user_answer = user_answers[i-1]
                            correct_answer = question.get('correct_answer', '')
                            
                            if option_key == correct_answer:
                                prefix = f"✓ {option_key}. "  # Correct answer
                            elif option_key == user_answer and user_answer != correct_answer:
                                prefix = f"✗ {option_key}. "  # Wrong user answer
                        
                        story.append(Paragraph(f"{prefix}{option_text}", style))
                
                # Explanation (if available)
                if question.get('explanation'):
                    story.append(Spacer(1, 8))
                    story.append(Paragraph(f"<b>Explanation:</b> {question['explanation']}", 
                                         self.custom_styles['quote']))
                
                story.append(Spacer(1, 15))
        
        # Answer key section (if no user answers provided)
        if not user_answers and quiz_data.get('questions'):
            story.append(PageBreak())
            story.append(Paragraph("Answer Key", self.custom_styles['title']))
            story.append(Spacer(1, 20))
            
            for i, question in enumerate(quiz_data['questions'], 1):
                correct_answer = question.get('correct_answer', 'N/A')
                story.append(Paragraph(f"<b>Question {i}:</b> {correct_answer}", 
                                     self.custom_styles['body']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_report_pdf(self, content, summary_data, notes_data, quiz_data):
        """Generate comprehensive report PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Build story
        story = []
        
        # Title page
        story.append(Paragraph("Study Report", self.custom_styles['title']))
        story.append(Spacer(1, 30))
        
        if content.get('title'):
            story.append(Paragraph(content['title'], self.custom_styles['subtitle']))
            story.append(Spacer(1, 20))
        
        story.append(Paragraph(f"<b>Generated on:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                             self.custom_styles['body']))
        story.append(Spacer(1, 30))
        
        # Table of contents
        story.append(Paragraph("Table of Contents", self.custom_styles['section']))
        story.append(Paragraph("1. Summary", self.custom_styles['body']))
        story.append(Paragraph("2. Study Notes", self.custom_styles['body']))
        story.append(Paragraph("3. Practice Quiz", self.custom_styles['body']))
        story.append(PageBreak())
        
        # Summary section
        story.append(Paragraph("1. Summary", self.custom_styles['title']))
        story.append(Spacer(1, 20))
        
        if summary_data:
            if summary_data.get('main_topic'):
                story.append(Paragraph("Main Topic", self.custom_styles['section']))
                story.append(Paragraph(summary_data['main_topic'], self.custom_styles['body']))
                story.append(Spacer(1, 15))
            
            if summary_data.get('key_points'):
                story.append(Paragraph("Key Points", self.custom_styles['section']))
                for point in summary_data['key_points']:
                    story.append(Paragraph(f"• {point}", self.custom_styles['list_item']))
                story.append(Spacer(1, 15))
        
        story.append(PageBreak())
        
        # Notes section
        story.append(Paragraph("2. Study Notes", self.custom_styles['title']))
        story.append(Spacer(1, 20))
        
        if notes_data and notes_data.get('sections'):
            for section in notes_data['sections']:
                story.append(Paragraph(section.get('heading', 'Section'), self.custom_styles['section']))
                if section.get('content'):
                    story.append(Paragraph(section['content'], self.custom_styles['body']))
                story.append(Spacer(1, 15))
        
        story.append(PageBreak())
        
        # Quiz section
        story.append(Paragraph("3. Practice Quiz", self.custom_styles['title']))
        story.append(Spacer(1, 20))
        
        if quiz_data and quiz_data.get('questions'):
            for i, question in enumerate(quiz_data['questions'], 1):
                story.append(Paragraph(f"<b>Question {i}:</b> {question.get('question', '')}", 
                                     self.custom_styles['body']))
                story.append(Spacer(1, 10))
                
                if question.get('options'):
                    for option_key, option_text in question['options'].items():
                        story.append(Paragraph(f"{option_key}. {option_text}", self.custom_styles['list_item']))
                
                story.append(Spacer(1, 15))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
