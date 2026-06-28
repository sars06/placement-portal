# Placement Portal

A full-stack web application that streamlines the campus recruitment process by providing a centralized platform for **Students**, **Companies**, and **Administrators**.
The system simplifies placement management by allowing companies to publish recruitment drives, students to apply online, and administrators to monitor and manage the complete placement workflow through an intuitive dashboard.

## Table of Contents

* Overview
* Problem Statement
* Features
* User Roles
* Technologies Used
* System Architecture
* Database Schema
* Running the Project
* Deployment
* API Routes
* Screenshots
* Future Improvements
* Author

# Overview

Campus placement activities often involve multiple manual processes such as collecting resumes, announcing job drives, tracking applications, and communicating results. Managing these activities manually becomes inefficient as the number of students and companies increases.
The Placement Portal digitizes the complete placement workflow by providing role-based dashboards for Students, Companies, and Administrators.

# Problem Statement

Design and develop a centralized web-based platform that streamlines the campus placement process by connecting students, companies, and administrators.

The system should enable:

* Companies to register and publish placement drives
* Students to browse available opportunities and apply
* Administrators to monitor and manage the complete recruitment lifecycle

# Features

##  Student Module

* Student Registration
* Secure Login
* Student Dashboard
* Edit Profile
* Upload Resume
* Browse Placement Drives
* Search Available Drives
* Apply to Placement Drives
* Track Application Status
* View Application History

---

##  Company Module

* Company Registration
* Login
* Company Dashboard
* Post New Placement Drives
* View Posted Drives
* View Applicants
* Shortlist Candidates
* Select Candidates
* Reject Candidates

##  Admin Module

* Secure Admin Login
* Dashboard Analytics
* Approve Companies
* Reject Companies
* View All Students
* Search Students
* Filter Students by Branch
* View Student Profiles
* Blacklist / Unblock Students
* View Placement Drives
* Approve Drives
* Reject Drives
* View Drive Details
* Monitor Applications

#  Technologies Used

## Backend

* Flask
* SQLAlchemy
* Jinja2
* Flask Session

## Frontend

* HTML5
* CSS3
* Bootstrap 5
* Jinja Templates

## Database

### Development

SQLite

### Production

PostgreSQL (Render)


#  System Architecture

                ---------------------
                |      Browser      |
                ---------------------
                          |
                     Flask Server
                          |
         -----------------+-----------------
         |                                 |
     Jinja Templates                 SQLAlchemy ORM
         |                                 |
         -----------------+-----------------
                          |
                    SQLite / PostgreSQL

#  User Roles

## Student

Students can:

* Register
* Login
* Complete Profile
* Upload Resume
* Browse Drives
* Apply to Drives
* Track Application Status

## Company

Companies can:

* Register
* Await Admin Approval
* Login
* Create Placement Drives
* View Applicants
* Manage Candidate Status

## Administrator

Administrators can:

* Manage Students
* Manage Companies
* Manage Drives
* Approve Registrations
* Reject Drives
* Monitor Applications
* Blacklist Students

#  Database Schema

## User

| Field    | Type    |
| -------- | ------- |
| id       | Integer |
| username | String  |
| password | String  |
| role     | String  |


## Student

| Field           |
| --------------- |
| Roll Number     |
| Full Name       |
| Email           |
| Phone           |
| Branch          |
| CGPA            |
| Graduation Year |
| Resume          |
| Status          |


## Company

| Field        |
| ------------ |
| Company ID   |
| Username     |
| Company Name |
| HR Name      |
| Email        |
| Phone        |
| Website      |
| Industry     |
| Description  |
| Location     |
| Status       |

## Drive

Contains:

* Job Title
* Description
* Eligibility
* Package
* Location
* Deadline
* Minimum CGPA
* Eligible Branches
* Skills Required
* Job Type
* Work Mode
* Bond
* Status

---

## Application

Contains:

* Student
* Drive
* Application Status

---

#  Project Structure

```
PlacementPortal/
│
├── app.py
├── model.py
├── requirements.txt
├── Procfile
│
├── instance/
│
├── static/
│   ├── css/
│   ├── resumes/
│   └── images/
│
├── templates/
│   ├── admin_dashboard.html
│   ├── admin_students.html
│   ├── admin_companies.html
│   ├── admin_drives.html
│   ├── student_dashboard.html
│   ├── student_drives.html
│   ├── student_profile.html
│   ├── company_dashboard.html
│   ├── company_applications.html
│   ├── login.html
│   └── ...
│
└── README.md
```

#  Running the Project

Start the Flask server

python app.py


Open

http://127.0.0.1:5000


#  Deployment

The project is configured for deployment on **Render**.

Production uses:

* Gunicorn
* PostgreSQL
* Environment Variables

Required Environment Variables

DATABASE_URL
SECRET_KEY

#  Main Routes

| Route                 | Description          |
| --------------------- | -------------------- |
| /login                | Login                |
| /logout               | Logout               |
| /register/student     | Student Registration |
| /register/company     | Company Registration |
| /student/dashboard    | Student Dashboard    |
| /student/drives       | View Drives          |
| /student/history      | Application History  |
| /company/dashboard    | Company Dashboard    |
| /company/drive/create | Post Drive           |
| /admin/dashboard      | Admin Dashboard      |
| /admin/students       | Student Management   |
| /admin/companies      | Company Management   |
| /admin/drives         | Drive Management     |

#  Authentication

The system supports three different user roles.

* Student
* Company
* Administrator

Each role has access only to its authorized pages through session-based authentication.

#  Future Improvements

* Email Notifications
* Resume Parsing
* Interview Scheduling
* AI Resume Screening
* Skill Matching
* Company Ratings
* Student Recommendation System
* Placement Analytics
* CSV/Excel Export
* REST API
* JWT Authentication
* Docker Deployment
* Multi-College Support

##  If you found this project useful, consider giving it a star on GitHub!
