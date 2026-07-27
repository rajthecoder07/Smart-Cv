import re
import os
import io
import json
import random
import hashlib
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pdfplumber
from google import genai

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import resume helpers
from resume_helpers import ResumeBuilder, init_resume_tables, create_resume, get_resume, update_resume, get_user_resumes, delete_resume

# ================= SETUP =================

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = None

try:
    if GEMINI_API_KEY:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print("Gemini initialization failed:", e)

app = Flask(__name__)
app.secret_key = "smartcv_secret_key_2024"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

# ================= DATABASE =================

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT UNIQUE,
            full_name TEXT,
            created_at TEXT
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            job_title TEXT,
            score INTEGER,
            matched_skills TEXT,
            missing_skills TEXT,
            timestamp TEXT
        )''')
        
        # Initialize resume tables
        init_resume_tables(cursor)

        conn.commit()
    finally:
        conn.close()

init_db()

# ================= HELPERS =================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)
    return text

def extract_skills(text):
    skills_db = [
        "python", "java", "javascript", "typescript", "kotlin", "swift",
        "c", "c++", "c#", "php", "ruby", "go", "rust", "scala", "r",
        "html", "css", "react", "angular", "vue", "bootstrap", "tailwind",
        "webpack", "redux", "jquery", "sass", "responsive design",
        "node.js", "django", "flask", "spring boot", "express", "fastapi",
        "rest api", "graphql", "microservices", "mvc",
        "sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle",
        "redis", "firebase", "elasticsearch", "database design",
        "machine learning", "deep learning", "nlp", "data analysis",
        "data science", "pandas", "numpy", "matplotlib", "seaborn",
        "scikit-learn", "tensorflow", "keras", "pytorch", "opencv",
        "statistics", "data visualization", "power bi", "tableau",
        "computer vision", "transformers", "bert", "spacy", "nltk",
        "spark", "hadoop", "airflow", "kafka", "data engineering",
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
        "jenkins", "ci/cd", "linux", "bash", "git", "github", "gitlab",
        "networking", "security", "android", "ios", "react native",
        "flutter", "xml", "gradle", "xcode", "material design",
        "manual testing", "selenium", "automation", "testng", "cucumber",
        "postman", "api testing", "test cases", "bug reporting", "jira",
        "figma", "adobe xd", "photoshop", "illustrator", "canva",
        "ui design", "ux design", "wireframing", "prototyping",
        "accounting", "tally", "excel", "gst", "audit", "ms office",
        "financial modeling", "forecasting", "valuation", "budgeting",
        "seo", "sem", "google ads", "social media", "content marketing",
        "email marketing", "google analytics", "copywriting", "wordpress",
        "agile", "scrum", "jira", "confluence", "leadership",
        "recruitment", "hrms", "payroll", "onboarding",
        "ethical hacking", "kali linux", "metasploit", "burp suite",
        "penetration testing", "vulnerability assessment",
    ]
    found = []
    text = text.lower()
    for skill in skills_db:
        if skill in text:
            found.append(skill)
    return found

# ================= GEMINI AI =================

def analyze_with_gemini(resume_text):
    try:
        prompt = f"""
You are an expert resume analyzer and career coach with deep knowledge of the job market.

Carefully read this resume/profile and return ONLY a valid JSON object:
{{
    "best_job": "Most suitable real-world job title based on the resume",
    "score": 85,
    "matched_skills": ["skill1", "skill2", "skill3"],
    "missing_skills": ["skill4", "skill5"],
    "feedback": "2-3 lines of honest, specific professional feedback about this resume",
    "all_matches": [
        {{"job_title": "Best Job", "score": 85, "matched": ["skill1"], "missing": ["skill2"], "suggestions": ["specific actionable tip"]}},
        {{"job_title": "2nd Job", "score": 72, "matched": ["skill1"], "missing": ["skill3"], "suggestions": ["specific actionable tip"]}},
        {{"job_title": "3rd Job", "score": 65, "matched": ["skill1"], "missing": ["skill4"], "suggestions": ["specific actionable tip"]}},
        {{"job_title": "4th Job", "score": 55, "matched": ["skill1"], "missing": ["skill5"], "suggestions": ["specific actionable tip"]}},
        {{"job_title": "5th Job", "score": 45, "matched": ["skill1"], "missing": ["skill6"], "suggestions": ["specific actionable tip"]}},
        {{"job_title": "6th Job", "score": 35, "matched": ["skill1"], "missing": ["skill7"], "suggestions": ["specific actionable tip"]}}
    ]
}}

STRICT RULES:
- Analyze deeply and intelligently based ONLY on what is written in the resume
- Do NOT limit yourself to any fixed list of jobs — suggest the most relevant real-world job titles freely
- score is out of 100, based on how well the resume fits each job
- all_matches must have exactly 6 DIFFERENT job roles sorted by score descending
- matched_skills = skills/technologies actually present in the resume
- missing_skills = important skills missing for the best_job
- suggestions in all_matches must be specific and actionable (not generic)
- feedback must be honest, specific, and helpful
- Return ONLY the JSON object — no markdown, no extra text, no explanation

Resume/Profile:
{resume_text}
"""
        response = gemini_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"[GEMINI ERROR]: {type(e).__name__}: {e}")
        return None


def generate_ai_feedback_gemini(job_role, resume_text):
    """Use Gemini to generate detailed resume feedback for a specific job role."""
    try:
        prompt = f"""
You are an expert resume coach and ATS specialist.

Analyze this resume for the role of "{job_role}" and return ONLY a valid JSON object:
{{
    "score": 7.5,
    "strengths": ["strength1", "strength2", "strength3"],
    "improvements": ["improvement1", "improvement2", "improvement3"],
    "suggested_lines": ["bullet point for resume 1", "bullet point 2", "bullet point 3"],
    "missing_ats_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
    "pro_tips": ["tip1", "tip2", "tip3"]
}}

RULES:
- score is out of 10
- strengths: what is good in the resume for this role (be specific)
- improvements: what must be improved (be specific, not generic)
- suggested_lines: strong resume bullet points the person can directly add
- missing_ats_keywords: important keywords missing for "{job_role}" role
- pro_tips: practical tips to improve this specific resume
- Return ONLY JSON, no extra text

Job Role: {job_role}

Resume:
{resume_text}
"""
        response = gemini_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"[GEMINI FEEDBACK ERROR]: {e}")
        return None


def generate_career_chat_response(user_message, analysis=None):
    """Generate a career chat response using Gemini."""
    try:
        context_text = ""
        if analysis:
            target = analysis.get('target_result', {})
            context_text = (
                f"Best job: {target.get('job_title', 'Unknown')}\n"
                f"Score: {target.get('score', 0)}\n"
                f"Matched Skills: {', '.join(target.get('matched', []))}\n"
                f"Missing Skills: {', '.join(target.get('missing', []))}\n"
                f"Feedback: {target.get('suggestions', [''])[0]}\n"
            )

        prompt = f"""
You are an expert career coach and resume advisor. Answer the user's question clearly and helpfully.

Context:
{context_text}

User question:
{user_message}

Provide a concise, actionable answer and professional career advice.
Return ONLY the answer, with no markdown formatting.
"""
        response = gemini_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        text = text.replace("```", "").strip()
        return text
    except Exception as e:
        print(f"[GEMINI CHAT ERROR]: {e}")
        return None


# ================= TEMPLATE HELPERS =================

def load_resume_templates():
    """Load resume templates from JSON file."""
    templates_path = os.path.join(BASE_DIR, 'data', 'resume_templates.json')
    try:
        with open(templates_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[RESUME TEMPLATE LOAD ERROR]: {e}")
        return []


def load_prefilled_samples():
    """Load prefilled professional resume samples."""
    samples_path = os.path.join(BASE_DIR, 'data', 'prefilled_samples.json')
    try:
        with open(samples_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"[PREFILLED LOAD ERROR]: {e}")
        return []


# ================= ROUTES =================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username  = request.form.get('username', '').strip()
        password  = request.form.get('password', '').strip()
        email     = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip()

        if not username or not password or not email or not full_name:
            flash("All fields are required!", "danger")
            return render_template('register.html')

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                flash("This username is already taken!", "danger")
                return render_template('register.html')

            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                flash("This email is already registered!", "danger")
                return render_template('register.html')

            cursor.execute('''
                INSERT INTO users (username, password, email, full_name, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, hash_password(password), email, full_name, datetime.now()))
            conn.commit()
            session['username'] = username
            return redirect(url_for('dashboard'))

        except Exception as e:
            print(f"[REGISTER ERROR]: {e}")
            flash(f"Something went wrong: {str(e)}", "danger")
        finally:
            conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                           (request.form['username'], hash_password(request.form['password'])))
            user = cursor.fetchone()
        finally:
            conn.close()
               
        if user:
            session['username'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password!", "danger")

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT job_title, score, timestamp FROM results
            WHERE username=? ORDER BY id DESC LIMIT 3
        ''', (session['username'],))
        recent = cursor.fetchall()
    finally:
        conn.close()

    return render_template('dashboard.html', recent=recent)


@app.route('/upload-pdf', methods=['GET', 'POST'])
def upload_pdf():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files.get('resume_pdf')

        if not file or file.filename == '':
            flash("Please select a PDF file!", "danger")
            return redirect(url_for('upload_pdf'))

        text = ""
        try:
            with pdfplumber.open(io.BytesIO(file.read())) as pdf:
                for page in pdf.pages:
                    if page.extract_text():
                        text += page.extract_text()
        except:
            flash("Invalid PDF! Please upload a valid PDF file.", "danger")
            return redirect(url_for('upload_pdf'))

        if not text.strip():
            flash("No text found in PDF! Please upload a text-based PDF.", "danger")
            return redirect(url_for('upload_pdf'))

        # Gemini AI Analysis
        ai_result = analyze_with_gemini(text)

        if ai_result:
            print(f"✅ Gemini analyzed: {ai_result.get('best_job')} — {ai_result.get('score')}%")
            top_job      = ai_result.get("best_job", "Unknown")
            top_score    = ai_result.get("score", 0)
            top_matched  = ai_result.get("matched_skills", [])
            top_missing  = ai_result.get("missing_skills", [])
            top_feedback = ai_result.get("feedback", "")

            session['analysis'] = {
                "target_result": {
                    "job_title":      top_job,
                    "score":          top_score,
                    "matched":        top_matched,
                    "missing":        top_missing,
                    "suggestions":    [top_feedback],
                    "description":    "",
                    "total_required": len(top_matched) + len(top_missing)
                },
                "all_scores":  ai_result.get("all_matches", []),
                "ai_powered":  True
            }
        else:
            flash("AI analysis failed. Please try again.", "danger")
            return redirect(url_for('upload_pdf'))

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO results (username, job_title, score, matched_skills, missing_skills, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session['username'], top_job, top_score,
                ', '.join(top_matched), ', '.join(top_missing), datetime.now()
            ))
            conn.commit()
        finally:
            conn.close()

        return redirect(url_for('results'))

    return render_template('upload_pdf.html')


@app.route('/results')
def results():
    data = session.get('analysis')
    if not data:
        flash("No analysis found! Please submit your resume first.", "warning")
        return redirect(url_for('dashboard'))
    return render_template('results.html', data=data)


@app.route('/resume-form', methods=['GET', 'POST'])
def resume_form():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name       = request.form.get('name', '').strip()
        skills     = request.form.get('skills', '').strip()
        experience = request.form.get('experience', '').strip()
        education  = request.form.get('education', '').strip()

        if not skills:
            flash("Please enter your skills!", "danger")
            return redirect(url_for('resume_form'))

        # Build a rich text for Gemini to analyze
        full_text = f"""
Name: {name}
Skills: {skills}
Experience: {experience}
Education: {education}
""".strip()

        ai_result = analyze_with_gemini(full_text)

        if ai_result:
            top_job     = ai_result.get("best_job", "Unknown")
            top_score   = ai_result.get("score", 0)
            top_matched = ai_result.get("matched_skills", [])
            top_missing = ai_result.get("missing_skills", [])

            session['analysis'] = {
                "target_result": {
                    "job_title":      top_job,
                    "score":          top_score,
                    "matched":        top_matched,
                    "missing":        top_missing,
                    "suggestions":    [ai_result.get("feedback", "")],
                    "description":    "",
                    "total_required": len(top_matched) + len(top_missing)
                },
                # ✅ Fixed: Use Gemini's all_matches, NOT keyword database
                "all_scores":  ai_result.get("all_matches", []),
                "ai_powered":  True
            }
        else:
            flash("AI analysis failed. Please try again.", "danger")
            return redirect(url_for('resume_form'))

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO results (username, job_title, score, matched_skills, missing_skills, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session['username'], top_job, top_score,
                ', '.join(top_matched), ', '.join(top_missing), datetime.now()
            ))
            conn.commit()
        finally:
            conn.close()

        return redirect(url_for('results'))

    return render_template('resume_form.html')


@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT job_title, score, matched_skills, missing_skills, timestamp
            FROM results WHERE username=? ORDER BY id DESC
        ''', (session['username'],))
        data = cursor.fetchall()
    finally:
        conn.close()

    return render_template('history.html', data=data)


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))


@app.route('/templates')
def template_gallery():
    """Display template gallery for resume templates."""
    if 'username' not in session:
        return redirect(url_for('login'))
    
    templates = load_resume_templates()
    prefilled_samples = load_prefilled_samples()
    return render_template('template_gallery.html', templates=templates, prefilled_samples=prefilled_samples)


@app.route('/api/resume-templates')
def get_resume_templates():
    """API endpoint to get all resume templates."""
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    templates = load_resume_templates()
    return jsonify(templates)


@app.route('/api/select-template', methods=['POST'])
def select_template():
    """API endpoint to store selected template (handled via localStorage on client)."""
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    template_id = data.get('template_id', '')
    
    templates = load_resume_templates()
    template = next((t for t in templates if t['id'] == template_id), None)
    
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    return jsonify({'success': True, 'template': template})


@app.route('/ai-feedback', methods=['GET', 'POST'])
def ai_feedback():
    if 'username' not in session:
        return redirect(url_for('login'))

    feedback = None

    if request.method == 'POST':
        job_role = request.form.get('job_role', '').strip()

        if not job_role:
            flash("Job Role is required!", "danger")
            return redirect(url_for('ai_feedback'))

        resume_text = ""
        file = request.files.get('resume_pdf')

        if file and file.filename != '':
            try:
                with pdfplumber.open(io.BytesIO(file.read())) as pdf:
                    for page in pdf.pages:
                        if page.extract_text():
                            resume_text += page.extract_text()
            except:
                flash("Invalid PDF! Please upload a valid PDF.", "danger")
                return redirect(url_for('ai_feedback'))

            if not resume_text.strip():
                flash("No text found in PDF!", "danger")
                return redirect(url_for('ai_feedback'))
        else:
            skills     = request.form.get('skills', '').strip()
            experience = request.form.get('experience', '').strip()
            education  = request.form.get('education', '').strip()
            resume_text = f"Skills: {skills}\nExperience: {experience}\nEducation: {education}"

        # ✅ Use Gemini for feedback
        # If the Gemini client is not initialized, show a helpful message instead of failing silently
        if gemini_client is None:
            print("[GEMINI FEEDBACK ERROR]: Gemini client not configured (missing GEMINI_API_KEY).")
            flash("AI service not configured. Please set GEMINI_API_KEY in your .env and restart the app.", "danger")
            return render_template('ai_feedback.html', feedback=None)

        gemini_feedback = generate_ai_feedback_gemini(job_role, resume_text)

        if gemini_feedback:
            score       = gemini_feedback.get("score", 0)
            strengths   = gemini_feedback.get("strengths", [])
            improvements = gemini_feedback.get("improvements", [])
            suggested   = gemini_feedback.get("suggested_lines", [])
            missing_kw  = gemini_feedback.get("missing_ats_keywords", [])
            pro_tips    = gemini_feedback.get("pro_tips", [])

            feedback = f"""⭐ Overall Score: {score}/10

✅ Strengths:
{chr(10).join('- ' + s for s in strengths)}

🔧 Improvements Needed:
{chr(10).join('- ' + i for i in improvements)}

📝 Suggested Resume Lines:
{chr(10).join('- ' + l for l in suggested)}

🔑 Missing ATS Keywords ({job_role}):
{chr(10).join('- ' + k for k in missing_kw) if missing_kw else '- All important keywords are present!'}

💡 Pro Tips:
{chr(10).join('- ' + t for t in pro_tips)}"""
        else:
            flash("AI feedback failed. Please try again.", "danger")
            return redirect(url_for('ai_feedback'))

    return render_template('ai_feedback.html', feedback=feedback)


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.args.get('clear'):
        session.pop('chat_history', None)
        return redirect(url_for('chat'))

    chat_history = session.get('chat_history', [])

    if request.method == 'POST':
        user_message = request.form.get('message', '').strip()
        if not user_message:
            flash('Please enter a message to continue the career chat.', 'warning')
            return redirect(url_for('chat'))

        if gemini_client is None:
            print('[GEMINI CHAT ERROR]: Gemini client not configured (missing GEMINI_API_KEY).')
            flash('AI service not configured. Please set GEMINI_API_KEY in your .env and restart the app.', 'danger')
            return redirect(url_for('chat'))

        bot_response = generate_career_chat_response(user_message, session.get('analysis'))
        if bot_response is None:
            flash('AI career chat failed. Please try again.', 'danger')
            return redirect(url_for('chat'))

        chat_history.append({'role': 'user', 'text': user_message})
        chat_history.append({'role': 'assistant', 'text': bot_response})
        session['chat_history'] = chat_history

    return render_template('chat.html', messages=chat_history)


# ================= RUN =================

if __name__ == '__main__':
    app.run(debug=True)