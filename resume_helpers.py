import os
import json
import base64
import mimetypes
from datetime import datetime
from PIL import Image
import io

# ==================== HELPERS ====================

class ResumeBuilder:
    """Helper class for managing resumes and templates"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.uploads_dir = os.path.join(base_dir, 'static', 'uploads', 'profile_images')
        self.ensure_dirs()
    
    def ensure_dirs(self):
        """Create necessary directories"""
        os.makedirs(self.uploads_dir, exist_ok=True)
    
    def load_template_config(self):
        """Load template configuration"""
        config_path = os.path.join(self.base_dir, 'data', 'template_config.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def load_form_fields(self):
        """Load form field definitions"""
        fields_path = os.path.join(self.base_dir, 'data', 'form_fields.json')
        try:
            with open(fields_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def get_template_html_file(self, template_id):
        """Get template HTML file path"""
        template_map = {
            'sidebar-professional': 'resume_template_sidebar.html',
            'modern-clean': 'resume_template_modern.html',
            'modern-v2': 'resume_template_modern_v2.html',
            'header-professional': 'resume_template_header.html',
            'header': 'resume_template_header.html',
            'minimal-clean': 'resume_template_minimal.html',
            'minimal': 'resume_template_minimal.html'
        }
        return template_map.get(template_id, None)
    
    def validate_image(self, file):
        """Validate uploaded image file"""
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        max_size = 5 * 1024 * 1024  # 5MB
        
        # Check file size
        if len(file.getvalue()) > max_size:
            return False, "File size exceeds 5MB limit"
        
        # Check file extension
        filename = file.filename.lower()
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            return False, "Only JPG, JPEG, PNG files are allowed"
        
        try:
            # Verify it's a valid image
            img = Image.open(io.BytesIO(file.getvalue()))
            img.verify()
            file.seek(0)  # Reset file pointer
            return True, "Valid image"
        except:
            return False, "Invalid image file"
    
    def process_profile_image(self, file, resume_id, user_id):
        """Process and save profile image, return base64"""
        try:
            # Validate
            valid, msg = self.validate_image(file)
            if not valid:
                return None, msg
            
            # Open and resize image
            img = Image.open(io.BytesIO(file.getvalue()))
            
            # Resize to standard size (150x150)
            img.thumbnail((150, 150), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Save to file system
            safe_filename = f"{user_id}_{resume_id}_{datetime.now().timestamp()}.jpg"
            file_path = os.path.join(self.uploads_dir, safe_filename)
            img.save(file_path, 'JPEG', quality=90)
            
            # Convert to base64 for embedding
            img_io = io.BytesIO()
            img.save(img_io, 'JPEG', quality=85)
            img_io.seek(0)
            base64_str = base64.b64encode(img_io.getvalue()).decode()
            
            return f"data:image/jpeg;base64,{base64_str}", None
        
        except Exception as e:
            return None, f"Error processing image: {str(e)}"
    
    def validate_resume_data(self, data):
        """Validate resume data structure"""
        required_fields = {
            'personal': ['fullName', 'title', 'email'],
        }
        
        for field, required_subfields in required_fields.items():
            if field not in data:
                return False, f"Missing required field: {field}"
            
            for subfield in required_subfields:
                if subfield not in data.get(field, {}):
                    return False, f"Missing required field: {field}.{subfield}"
        
        return True, "Valid resume data"
    
    def create_default_resume_data(self):
        """Create default resume data structure"""
        return {
            'personal': {
                'fullName': '',
                'title': '',
                'email': '',
                'phone': '',
                'location': '',
                'profileImage': None
            },
            'profile': '',
            'skills': [],
            'languages': [],
            'experience': [],
            'education': [],
            'references': []
        }
    
    def format_resume_data_for_template(self, data):
        """Format resume data for Jinja2 template rendering"""
        formatted = {
            'personal': {
                'fullName': data.get('personal', {}).get('fullName', ''),
                'title': data.get('personal', {}).get('title', ''),
                'email': data.get('personal', {}).get('email', ''),
                'phone': data.get('personal', {}).get('phone', ''),
                'location': data.get('personal', {}).get('location', ''),
                'profileImage': data.get('personal', {}).get('profileImage', None)
            },
            'profile': data.get('profile', ''),
            'skills': data.get('skills', []),
            'languages': self._format_languages(data.get('languages', [])),
            'experience': data.get('experience', []),
            'education': data.get('education', []),
            'references': data.get('references', [])
        }
        return formatted
    
    def _format_languages(self, languages):
        """Format language data with proper level as integer"""
        formatted = []
        for lang in languages:
            formatted.append({
                'name': lang.get('name', ''),
                'level': min(5, max(1, int(str(lang.get('level', '3')).strip() or 3)))
            })
        return formatted

# ==================== DATABASE HELPERS ====================

def init_resume_tables(cursor):
    """Initialize resume-related database tables"""
    
    # Resumes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        template_id TEXT NOT NULL,
        resume_data TEXT,
        title TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (username) REFERENCES users(username)
    )''')
    
    # Resume versions (for undo/redo)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        version_number INTEGER,
        resume_data TEXT,
        created_at TEXT,
        FOREIGN KEY (resume_id) REFERENCES resumes(id)
    )''')
    
    # Profile images
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS profile_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        file_path TEXT,
        base64_data TEXT,
        created_at TEXT,
        FOREIGN KEY (resume_id) REFERENCES resumes(id)
    )''')

def create_resume(cursor, conn, username, template_id, resume_data=None):
    """Create new resume"""
    if resume_data is None:
        resume_data = ResumeBuilder(os.path.dirname(__file__)).create_default_resume_data()

    try:
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user_row = cursor.fetchone()
        if not user_row:
            print(f"[CREATE RESUME ERROR]: User not found for username '{username}'")
            return None

        user_id = user_row[0]
        cursor.execute('''
            INSERT INTO resumes (user_id, username, template_id, resume_data, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            username,
            template_id,
            json.dumps(resume_data),
            resume_data.get('personal', {}).get('fullName', 'Untitled Resume'),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"[CREATE RESUME ERROR]: {e}")
        return None

def get_resume(cursor, resume_id):
    """Get resume by ID"""
    try:
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        result = cursor.fetchone()
        if result:
            cols = [description[0] for description in cursor.description]
            resume = dict(zip(cols, result))
            resume['resume_data'] = json.loads(resume['resume_data'])
            return resume
        return None
    except Exception as e:
        print(f"[GET RESUME ERROR]: {e}")
        return None

def update_resume(cursor, conn, resume_id, resume_data):
    """Update resume data"""
    try:
        cursor.execute('''
            UPDATE resumes
            SET resume_data = ?, updated_at = ?
            WHERE id = ?
        ''', (
            json.dumps(resume_data),
            datetime.now().isoformat(),
            resume_id
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"[UPDATE RESUME ERROR]: {e}")
        return False

def get_user_resumes(cursor, username):
    """Get all resumes for a user"""
    try:
        cursor.execute('''
            SELECT id, template_id, title, created_at, updated_at
            FROM resumes
            WHERE username = ?
            ORDER BY updated_at DESC
        ''', (username,))
        
        cols = [description[0] for description in cursor.description]
        resumes = [dict(zip(cols, row)) for row in cursor.fetchall()]
        return resumes
    except Exception as e:
        print(f"[GET USER RESUMES ERROR]: {e}")
        return []

def delete_resume(cursor, conn, resume_id):
    """Delete resume and related data"""
    try:
        cursor.execute('DELETE FROM profile_images WHERE resume_id = ?', (resume_id,))
        cursor.execute('DELETE FROM resume_versions WHERE resume_id = ?', (resume_id,))
        cursor.execute('DELETE FROM resumes WHERE id = ?', (resume_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"[DELETE RESUME ERROR]: {e}")
        return False
