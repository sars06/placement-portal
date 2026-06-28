from flask import Flask, render_template, request, redirect, session
from model import db, User, Student, Company, Drive, Application
from functools import wraps
from sqlalchemy import or_

app = Flask(__name__)
import os
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///instance/placement.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "secret")

db.init_app(app)

#auth
def login_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                return redirect('/login')
            return f(*args, **kwargs)
        return wrapper
    return decorator

#login
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        user = User.query.filter_by(
            username=username,
            password=password,
            role=role
        ).first()
        if not user:
            return "Invalid credentials"
        session['username'] = user.username
        session['role'] = user.role

        #admin login
        if role == 'admin':
            return redirect('/admin/dashboard')

        #student login
        elif role == 'student':
            student = Student.query.filter_by(roll_no=user.username).first()
            if not student:
                return "Student record not found (Contact admin)"
            if student.status == 'pending':
                return "Approval pending"
            elif student.status == 'rejected':
                return "Your account was rejected"
            elif student.status == 'blocked':
                return "You are blacklisted"
            elif student.status == 'approved':
                session['student_id'] = student.roll_no
                return redirect('/student/dashboard')
            else:
                return "Invalid status"
            
        #company login
        elif role == 'company':
            company = Company.query.filter_by(username=username).first()
            if not company:
                return "Company record not found"
            if company.status != 'approved':
                return " Your company is not approved yet"
            return redirect('/company/dashboard')
    return render_template('login.html', page_type="auth")

#logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

#register student
@app.route('/register/student', methods=['GET', 'POST'])
def register_student():
    if request.method == 'POST':
        roll_no = request.form['roll_number']
        password = request.form['password']
        existing_user = User.query.filter_by(username=roll_no).first()
        if existing_user:
            return "Roll number already registered."
        try:
            student = Student(
                roll_no=roll_no,
                full_name=request.form['full_name'],
                email=request.form['email'],
                phone=request.form.get('phone'),
                branch=request.form.get('branch'),
                cgpa=float(request.form.get('cgpa') or 0),
                grad_year=int(request.form.get('graduation_year') or 0),
                status='pending'
            )
            user = User(
                username=roll_no,  
                password=password,
                role='student'
            )
            db.session.add(student)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        except Exception as e:
            print("ERROR:", e)
            return str(e)
    return render_template('register_student.html')

#student dashboard
@app.route('/student/dashboard')
@app.route('/student/dashboard/<roll_no>')
def student_dashboard(roll_no=None):
    if roll_no:
        if session.get('role') != 'admin':
            return redirect('/login')
        student = Student.query.get(roll_no)
    else:
        if 'student_id' not in session:
            return redirect('/login')
        student = Student.query.get(session['student_id'])
    drives = Drive.query.filter_by(status='approved').all()
    apps = Application.query.filter_by(
        student_roll=student.roll_no
    ).all()
    return render_template(
        'student_dashboard.html',
        student=student,
        drives=drives,
        applications=apps,
        selections=len([a for a in apps if a.status == 'Selected'])
    )

#student drives
@app.route('/student/drives')
def student_drives():
    if 'student_id' not in session:
        return redirect('/login')
    drives = Drive.query.filter_by(status='approved').all()
    companies = {c.id: c for c in Company.query.all()}
    return render_template(
        'student_drives.html',
        drives=drives,
        companies=companies  
    )
    
#student app history
@app.route('/student/history')
def student_history():
    if 'student_id' not in session:
        return redirect('/login')
    apps = Application.query.filter_by(
        student_roll=session['student_id']   
    ).all()
    return render_template(
        'student_history.html',
        applications=apps,
        Company=Company
    )

#admin drive detail   
@app.route('/admin/drive/<int:id>')
def admin_drive_detail(id):
    drive = Drive.query.get_or_404(id)
    company = Company.query.get(drive.company_id)
    return render_template(
        'admin_drive_detail.html',
        drive=drive,
        company=company
    )

#admin approve drive
@app.route('/admin/drive/approve/<int:id>')
def approve_drive(id):
    drive = Drive.query.get_or_404(id)
    drive.status = 'approved'
    db.session.commit()
    return redirect('/admin/drives')

#student prof
@app.route('/student/profile', methods=['GET', 'POST'])
def student_profile():
    if 'username' not in session or session.get('role') != 'student':
        return redirect('/login')
    student = Student.query.filter_by(roll_no=session['username']).first()
    if request.method == 'POST':
        student.full_name = request.form['full_name']
        student.email = request.form['email']
        student.phone = request.form['phone']
        student.branch = request.form['branch']
        student.cgpa = float(request.form['cgpa'])
        db.session.commit()
        return redirect('/student/dashboard')
    return render_template('student_profile.html', student=student)

#apply drive
@app.route('/apply/<int:drive_id>')
def apply_drive(drive_id):
    if 'student_id' not in session:
        return redirect('/login')
    existing = Application.query.filter_by(
        student_roll=session['student_id'],
        drive_id=drive_id
    ).first()
    if existing:
        return "Already applied"
    new_app = Application(
        student_roll=session['student_id'],   
        drive_id=drive_id,
        status='Applied'
    )
    db.session.add(new_app)
    db.session.commit()
    print("NEW APPLICATION ADDED")  
    return redirect('/student/dashboard')

#resume
import os
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'static/resumes'
@app.route('/student/upload_resume', methods=['POST'])
def upload_resume():
    if 'username' not in session or session.get('role') != 'student':
        return redirect('/login')
    file = request.files.get('resume')
    if not file or file.filename == '':
        return "No file selected"
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    student = Student.query.filter_by(roll_no=session['username']).first()
    student.resume = filename
    db.session.commit()
    return redirect('/student/profile')

#company dashboard
@app.route('/company/dashboard')
def company_dashboard():
    if session.get('role') != 'company':
        return redirect('/login')
    username = session.get('username')
    company = Company.query.filter_by(username=username).first()
    if not company:
        return "Company not found"
    if company.status != 'approved':
        return "Waiting for admin approval"
    drives = Drive.query.filter_by(company_id=company.id).all()
    total_applicants = 0
    for d in drives:
        total_applicants += Application.query.filter_by(drive_id=d.id).count()
    return render_template(
        'company_dashboard.html',
        company=company,
        drives=drives,
        total=len(drives),
        applicants=total_applicants,
        page_type='dashboard'
    ) 
    
#company app status     
@app.route('/company/application/<int:id>/<status>')
def update_application(id, status):
    app = Application.query.get(id)
    app.status = status
    db.session.commit()
    return redirect(request.referrer)
    
#post drive
@app.route('/company/post', methods=['POST'])
@login_required('company')
def post_drive():
    d = Drive(
        company_id=request.form['company_id'],
        job_title=request.form['job_title'],
        package=request.form['package'],
        location=request.form['location'],
        deadline=request.form['deadline']
    )
    db.session.add(d)
    db.session.commit()
    return redirect('/company/dashboard')

#create drive
@app.route('/company/drive/create', methods=['GET', 'POST'])
def create_drive():
    if session.get('role') != 'company':
        return redirect('/login')
    username = session.get('username')
    company = Company.query.filter_by(username=username).first()
    if not company:
        return "Company not found"
    if request.method == 'POST':
        drive = Drive(
            job_title=request.form['job_title'],
            description=request.form['description'],
            package=request.form['package'],
            location=request.form['location'],
            deadline=request.form['deadline'],
            company_id=company.id,
            cgpa=request.form['cgpa'],
            batch=request.form['batch'],
            branches=request.form['branches'],
            skills=request.form['skills'],
            job_type=request.form['job_type'],
            mode=request.form['mode'],
            bond=request.form['bond'],
        )
        db.session.add(drive)
        db.session.commit()
        return redirect('/company/dashboard')
    return render_template('create_drive.html', page_type='dashboard')

#company drive app
@app.route('/company/drive/<int:drive_id>/applications')
def company_applications(drive_id):
    apps = Application.query.filter_by(drive_id=drive_id).all()
    return render_template(
        'company_applications.html',
        apps=apps,
        page_type='dashboard'
    )

#admin company approve
@app.route('/admin/company/approve/<int:id>')
def approve_company(id):
    company = Company.query.get(id)
    if not company:
        return "Company not found"
    company.status = 'approved'
    db.session.commit()
    return redirect('/admin/companies')

#reject company admin
@app.route('/admin/company/reject/<int:id>')
def reject_company(id):
    company = Company.query.get(id)
    if not company:
        return "Company not found"
    company.status = 'rejected'
    db.session.commit()
    return redirect('/admin/companies')

#admin dashbaord
@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    if session.get('role')!='admin':
        return redirect('/login')
    return render_template('admin_dashboard.html',
                           students_count=Student.query.count(),
                           companies_count=Company.query.count(),
                           drives_count=Drive.query.count(),
                           applications_count=Application.query.count(),
                           page_type="dashboard")

# admin students
@app.route('/admin/students')
@login_required('admin')
def admin_students():
    search = request.args.get('search', '').strip()
    branch = request.args.get('branch', '').strip()
    query = Student.query
    if search:
        query = query.filter(
            or_(
                Student.roll_no.ilike(f"%{search}%"),
                Student.full_name.ilike(f"%{search}%")
            )
        )
    if branch:
        query = query.filter(Student.branch == branch)
    students = query.order_by(Student.roll_no).all()
    return render_template(
        'admin_students.html',
        students=students,
        search=search,
        branch=branch
    )

#admin companies
@app.route('/admin/companies')
@login_required('admin')
def admin_companies():
    companies = Company.query.all()
    return render_template('admin_companies.html', companies=companies)

#admin company detsail
@app.route('/admin/company/<int:id>')
def view_company(id):
    if session.get('role') != 'admin':
        return redirect('/login')
    company = Company.query.get(id)
    return render_template('admin_company_detail.html', company=company)

#reject drive admin
@app.route('/admin/drive/reject/<int:id>')
def reject_drive(id):
    d = Drive.query.get(id)
    d.status = 'rejected'
    db.session.commit()
    return redirect('/admin/drives')


#shortlist
@app.route('/company/app/<int:id>/shortlist')
def shortlist(id):
    app = Application.query.get(id)
    app.status = 'Shortlisted'
    db.session.commit()
    return redirect(request.referrer)

#company reject
@app.route('/company/app/<int:id>/reject')
def reject_app(id):
    app = Application.query.get(id)
    app.status = 'Rejected'
    db.session.commit()
    return redirect(request.referrer)

#admin applications
@app.route('/admin/applications')
@login_required('admin')
def admin_applications():
    applications = db.session.query(Application, Student, Drive, Company)\
        .join(Student, Application.student_roll == Student.roll_no)\
        .join(Drive, Application.drive_id == Drive.id)\
        .join(Company, Drive.company_id == Company.id)\
        .all()
    return render_template('admin_applications.html', applications=applications)

#update app admin
@app.route('/admin/application/update/<int:id>/<status>')
@login_required('admin')
def update_application_status(id, status):
    app_obj = Application.query.get(id)
    app_obj.status = status
    db.session.commit()
    return redirect('/admin/applications')

#amdin student approve
@app.route('/admin/student/approve/<roll>')
@login_required('admin')
def approve_student(roll):
    s = Student.query.get(roll)
    s.status = 'approved'
    db.session.commit()
    return redirect('/admin/students')

#reect student admin
@app.route('/admin/student/reject/<roll>')
@login_required('admin')
def reject_student(roll):
    s = Student.query.get(roll)
    s.status = 'rejected'
    db.session.commit()
    return redirect('/admin/students')

#blacklist student
@app.route('/admin/student/blacklist/<roll>')
@login_required('admin')
def blacklist_student(roll):
    s = Student.query.get(roll)
    s.status = 'blacklisted'
    db.session.commit()
    return redirect('/admin/students')

#unblaclist student
@app.route('/admin/student/unblacklist/<roll>')
@login_required('admin')
def unblacklist_student(roll):
    s = Student.query.get(roll)
    s.status = 'approved'
    db.session.commit()
    return redirect('/admin/students')

#admin drives ongoing
@app.route('/admin/drives')
def admin_drives():
    if session.get('role') != 'admin':
        return redirect('/login')
    drives = Drive.query.all()
    companies = {
        c.id: c for c in Company.query.all()
    }
    return render_template(
        'admin_drives.html',
        drives=drives,
        companies=companies,  
        page_type='dashboard'
    )

#register company
@app.route('/register/company', methods=['GET', 'POST'])
def register_company():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        website = request.form.get('website')
        if not username or not password:
            return "Username and password are required"
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists"
        if website:
            website = website.strip()    
            if not website.startswith("http"):
                website = "https://" + website
            if not website.startswith("https://"):
                return "Only secure URLs (https://) are allowed"
        user = User(
            username=username,
            password=password,
            role='company'
        )
        company = Company(
            username=username,
            company_name=request.form.get('company_name'),
            hr_name=request.form.get('hr_name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            website=website,
            industry=request.form.get('industry'),
            description=request.form.get('description'),
            location=request.form.get('location'),
            status='pending'
        )
        try:
            db.session.add(user)
            db.session.add(company)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"
        return redirect('/login')
    return render_template('register_company.html')

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password="admin123", role="admin")
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)