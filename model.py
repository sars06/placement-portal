from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    role = db.Column(db.String(20))

class Student(db.Model):
    roll_no = db.Column(db.String(20), primary_key=True)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    branch = db.Column(db.String(50))
    cgpa = db.Column(db.Float)
    grad_year = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')  
    resume = db.Column(db.String(200))

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    company_name = db.Column(db.String(100))
    hr_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending', nullable=False)
    
class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer)
    job_title = db.Column(db.String(100))
    description = db.Column(db.Text)
    eligibility = db.Column(db.String(200))
    package = db.Column(db.String(50))
    location = db.Column(db.String(100))
    deadline = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')  
    cgpa = db.Column(db.String(10))
    batch = db.Column(db.String(10))
    branches = db.Column(db.String(200))
    skills = db.Column(db.String(200))
    job_type = db.Column(db.String(50))
    mode = db.Column(db.String(50))
    bond = db.Column(db.String(10))

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_roll = db.Column(
        db.String(20),
        db.ForeignKey('student.roll_no')
    )
    drive_id = db.Column(
        db.Integer,
        db.ForeignKey('drive.id')
    )
    status = db.Column(db.String(20), default="pending")
    student = db.relationship('Student', backref='applications')
    drive = db.relationship('Drive', backref='applications')