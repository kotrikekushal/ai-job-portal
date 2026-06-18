# AI-Powered Job Portal

## Overview

AI-Powered Job Portal is a full-stack recruitment platform built using Django REST Framework, MySQL, JWT Authentication, and Google Gemini AI.

The platform connects students, recruiters, and companies while providing intelligent resume analysis, ATS scoring, AI-powered job recommendations, interview question generation, and interview evaluation.

This project simulates a real-world hiring workflow from job posting to candidate selection.

---

## Features

### Authentication & Authorization

* JWT Authentication
* Student Registration & Login
* Recruiter Registration & Login
* Company Registration
* Protected APIs using Authentication

### Student Features

* View Available Jobs
* Search Jobs
* Filter Jobs
* Apply for Jobs
* Withdraw Applications
* View Applied Jobs
* Student Dashboard

### Recruiter Features

* Create Jobs
* Update Job Details
* Delete Jobs
* View Applicants
* Manage Application Status
* Recruiter Dashboard

### Company Features

* Company Registration
* Company Profile Management

---

## AI Features

### Resume Analysis

* PDF Resume Upload
* Resume Text Extraction using PyMuPDF
* AI Resume Analysis using Google Gemini

### ATS Scoring Engine

* Skill Matching Score
* Experience Score
* Education Score
* Certification Score
* Overall ATS Score

### Resume Feedback

* Strength Analysis
* Missing Skills Detection
* Improvement Suggestions

### AI Job Recommendations

* Personalized Job Recommendations
* Match Score Generation
* Recommendation Reasoning

### AI Interview System

* AI Interview Question Generation
* Easy, Medium, and Hard Questions
* Interview Evaluation
* Performance Feedback
* Hiring Recommendation

---

## Email Notifications

* Candidate Selection Emails
* Candidate Rejection Emails
* Automated Status Update Notifications

---

## Project Workflow

```text
Student Registration
        ↓
Resume Upload
        ↓
Resume Parsing
        ↓
AI Resume Analysis
        ↓
ATS Score Generation
        ↓
Job Application
        ↓
Recruiter Reviews Applicants
        ↓
Application Status Update
        ↓
Email Notification
```

---

## Project Architecture

### Student Module

* Registration
* Login
* Resume Management
* Job Search
* Applications
* Dashboard

### Recruiter Module

* Registration
* Login
* Job Management
* Applicant Management
* Dashboard

### Company Module

* Company Management
* Recruiter Association

### AI Module

* Resume Analysis
* ATS Engine
* Job Recommendation Engine
* Interview Engine

---

## Tech Stack

### Backend

* Python
* Django
* Django REST Framework

### Database

* MySQL

### Authentication

* JWT Authentication

### AI

* Google Gemini API

### Resume Processing

* PyMuPDF

### API Testing

* Postman / Thunder Client

### Version Control

* Git
* GitHub

---

## Database Models

* User
* StudentProfile
* RecruiterProfile
* Company
* Job
* Application

---

## Key Learning Outcomes

* Django REST Framework
* JWT Authentication
* API Development
* MySQL Integration
* Database Design
* File Upload Handling
* PDF Processing
* AI Integration
* ATS Scoring Systems
* Email Automation
* Authentication & Authorization
* REST API Testing
* Git & GitHub

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd ai-job-portal
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Database Migration

```bash
python manage.py migrate
```

### Run Server

```bash
python manage.py runserver
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

---

## Future Enhancements

* Resume Builder
* Interview Scheduling
* Real-Time Notifications
* Video Interview Support
* Advanced Analytics Dashboard
* Company Verification System
* Candidate Ranking System

---
