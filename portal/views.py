from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from .models import *
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from rest_framework.decorators import permission_classes
from .serializers import *
import fitz
from .skills import SKILLS
import google.generativeai as genai
import json
import re
from django.db.models import Q
from django.core.mail import send_mail
import os

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)
model = genai.GenerativeModel("gemini-2.5-flash")

@api_view(["POST"])
def Student_Signup(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")
    phone_number = request.data.get("phone_number")
    resume = request.data.get("resume")

    if User.objects.filter(username=username).exists():
        return Response({"error":"user already exists"})
    
    user =  User.objects.create_user(
        username=username,
        password=password,
        email=email,
    )
    StudentProfile.objects.create(
        user = user,
        phone_number=phone_number,
        resume=resume,
    )

    return Response({"message":"successfully created account"})

@api_view(["POST"])
def Company_Signup(request):
    company_name = request.data.get("company_name")
    company_email = request.data.get("company_email")
    company_website = request.data.get("company_website")
    company_description = request.data.get("company_description")
    company_location = request.data.get("company_location")

    
    if Company.objects.filter(company_name=company_name).exists():
        return Response({"error":"company  already exists"})
    
    Company.objects.create(
        company_name=company_name,
        company_location=company_location,
        company_description = company_description,
        company_email=company_email,
        company_website=company_website
    )
    return Response({"message":"successfully created company"})


@api_view(["POST"])
def Recruiter_Signup(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")
    phone_number = request.data.get("phone_number")
    desigination = request.data.get("designation")
    company_id = request.data.get("company")

    
    if User.objects.filter(username=username).exists():
        return Response({"error":"user already exists"})
    company = Company.objects.filter(id=company_id).first()

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
    )
    RecruiterProfile.objects.create(
        user=user,
        phone_number=phone_number,
        desigination=desigination,
        company=company
    )

    return Response({"message":"successfully created account"})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def Create_Job(request):
    job_title = request.data.get("job_title")
    job_description = request.data.get("job_description")
    required_skills = request.data.get("requried_skills")
    salary = request.data.get("salary")
    location = request.data.get("location")
    job_type = request.data.get("job_type")
    experience_required = request.data.get("experience_required")
    deadline = request.data.get("deadline")
    company_id = request.data.get("company")
    recruiter_id = request.data.get("recruiter")

    company = Company.objects.filter(id=company_id).first()
    recruiter = RecruiterProfile.objects.filter(id=recruiter_id).first()
    if not company:
        return Response({"error":"enter correct company id "})
    elif not recruiter:
         return Response({"error":"enter correct recruiter id "})

    
    Job.objects.create(
        job_title = job_title,
        job_description = job_description,
        required_skills = required_skills,
        salary = salary,
        location = location,
        job_type = job_type,
        experience_required = experience_required,
        deadline = deadline,
        company = company,
        recruiter = recruiter
    )

    return Response({"message":"successfully job created"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_jobs(request):
    jobs = Job.objects.all()

    serializer = JobSerializer(jobs,many=True)
    return Response(serializer.data)

def extract_resume_text(pdf_path):
    pdf = fitz.open(stream=pdf_path.read(),filetype="pdf")

    text = ""
    for page in pdf:
        text += page.get_text()
    return text


def extract_resume_data(resume_text):
    prompt = f"""
    Analyze this resume.

    Return ONLY valid JSON.

    Format:

    {{
        "name":"",
        "email":"",
        "phone":"",
        "skills": [],
        "projects": [],
        "education": "",
        "experience": "",
        "certifications": []
    }}

    Resume:

    {resume_text}
    """
    response = model.generate_content(prompt)
    response_text = response.text.strip()

    response_text = response_text.replace(
         "```json",
        ""
        )

    response_text = response_text.replace(
    "```",
    ""
    )
    data = json.loads(response_text)

    return data

def calculate_ats_score(resume_data,required_skills,experience_required):

    # Skills Score (60)

    resume_skills = [skill.lower()
        for skill in resume_data["skills"]
    ]

    required_skills = [skill.strip().lower()
        for skill in required_skills
    ]

    matched_skills = []
    missing_skills = []

    for skill in required_skills:

        if skill in resume_skills:
            matched_skills.append(skill)

        else:
            missing_skills.append(skill)

    if len(required_skills) > 0:

        skills_score = (len(matched_skills)/len(required_skills)) * 60

    else:
        skills_score = 0

    # Experience Score (20)

    experience_text = str(resume_data.get("experience",""))

    match = re.search(r"\d+",experience_text)

    resume_years = 0

    if match:
        resume_years = int(
            match.group()
        )

    required_years = int(experience_required)

    if required_years == 0:

        experience_score = 20

    elif resume_years >= required_years:

        experience_score = 20

    else:

        experience_score = (
            resume_years
            /
            required_years
        ) * 20

    # Education Score (10)

    education = str(resume_data.get("education","")).lower()

    if (
        "computer" in education
        or "engineering" in education
        or "b.tech" in education
        or "btech" in education
    ):

        education_score = 9

    else:

        education_score = 5

    # Certification Score (10)

    certifications = resume_data.get("certifications",[])

    cert_count = len(certifications)

    if cert_count >= 3:
        certification_score = 9

    elif cert_count == 2:
        certification_score = 8

    elif cert_count == 1:
        certification_score = 6

    else:
        certification_score = 0

    # Total Score

    total_score = (
        skills_score
        + experience_score
        + education_score
        + certification_score
    )

    return {

        "score": round(
            total_score,
            2
        ),

        "skills_score": round(
            skills_score,
            2
        ),

        "experience_score": round(
            experience_score,
            2
        ),

        "education_score": round(
            education_score,
            2
        ),

        "certification_score": round(
            certification_score,
            2
        ),

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills
    }

def generate_feedback(
    resume_data,
    ats_result
):

    prompt = f"""
You are an ATS Resume Reviewer.

Resume Data:

{resume_data}

ATS Result:

{ats_result}

Give response in JSON format:

{{
    "strengths": [],
    "missing_skills": [],
    "suggestions": []
}}

Rules:

1. Mention strengths.
2. Mention missing skills.
3. Suggest improvements.
4. Keep suggestions short.
5. Return ONLY JSON.
"""

    response = model.generate_content(
        prompt
    )

    response_text = response.text.strip()

    response_text = response_text.replace(
        "```json",
        ""
    )

    response_text = response_text.replace(
        "```",
        ""
    )

    return json.loads(
        response_text
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def analyze_resume(request):

    resume = request.FILES.get("resume")
    job_id = request.data.get("job_id")

    if not resume:
        return Response({
            "error":"Resume required"
        })

    job = Job.objects.filter(
        id=job_id
    ).first()

    if not job:
        return Response({
            "error":"Job not found"
        })

    # Step 1
    resume_text = extract_resume_text(
        resume
    )

    # Step 2
    resume_data = extract_resume_data(
        resume_text
    )

    # Step 3
    ats_result = calculate_ats_score(
        resume_data,
        job.required_skills.split(","),
        job.experience_required
    )

    # Step 4
    feedback = generate_feedback(
        resume_data,
        ats_result
    )

    return Response({

        "candidate": {
            "name": resume_data.get("name"),

            "email": resume_data.get("email"),

            "phone": resume_data.get("phone")
        },

        "ats_result":
            ats_result,

        "feedback":
            feedback
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def apply_job(request):
    job_id = request.data.get("job_id")

    job = Job.objects.filter(id=job_id).first()
    if not job:
        return Response({"error":"Job not found"})

    student = StudentProfile.objects.filter(user=request.user).first()
    application = Application.objects.filter(student=student,job=job).exists()
    if application:
        return Response({"error":"you have already applied to this job"})
    resume = student.resume

    resume_text = extract_resume_text(resume)
    resume_data = extract_resume_data(resume_text)

    ats_result = calculate_ats_score(resume_data,job.required_skills,job.experience_required)
    ats =ats_result["score"]
    Application.objects.create(
        student=student,
        job=job,
        ats_score=ats,
        status = "pending",
    )
    return Response({"message":"applied successfully ",
                     "ats_score":ats})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_applied_jobs(request):
    student = StudentProfile.objects.filter(user=request.user).first()
    applications = Application.objects.filter(student=student)
    jobs = []
    for i in applications:
        jobs.append((i.job.job_title,i.ats_score,i.status)) 
    
    return Response({"jobs":jobs})
    
@api_view(["POSt"])
@permission_classes([IsAuthenticated])
def view_applicants(request):
    job_id = request.data.get("job_id")
    job = Job.objects.filter(id=job_id).first()
    applications = Application.objects.filter(job=job).order_by("-ats_score")
    applicants = []
    for i in applications:
        applicants.append((i.student.user.username,i.ats_score,i.status)) 
    
    return Response({"applications":applicants})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def manage_application_status(request):
    student_id = request.data.get("student_id")
    job_id = request.data.get("job_id")
    status = request.data.get("status")
    student = StudentProfile.objects.filter(id=student_id).first()
    if not student:
        return Response({"error":"Student not found"})
    job = Job.objects.filter(id=job_id).first()
    if not job:
        return Response({"error":"Job not found"})
    application = Application.objects.filter(student=student,job=job).first()
    if not application:
        return Response({"error":"Application not found"})
    valid_status = [
        "Pending",
        "Selected",
        "Rejected",
        "Interview Scheduled"
    ]
    if status not in valid_status:
        return Response({"error":"Invalid status"})
    application.status = status
    application.save()

    if status == "Selected":
        send_mail(
        subject="Application Status Update",
        message=f"Congratulations! You have been selected for {job.job_title}.",
        from_email=None,
        recipient_list=[student.user.email]
    )
    if status == "Rejected":
        send_mail(
        subject="Application Status Update",
        message=f"Thank you for applying. Unfortunately, you were not selected for  {job.job_title}.",
        from_email=None,
        recipient_list=[student.user.email]
        )


    return Response({"message":"status changed successfully"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    student = StudentProfile.objects.filter(user=request.user).first()
    if not student:
        return Response({"error":"student not found"})
    applications = Application.objects.filter(student=student).count()
    if not applications:
        return Response({"total_applications":0,
                     "Selected":0,
                     "Rejected":0,
                     "Pending":0})
    selected = Application.objects.filter(student=student,status="selected").count()
    rejected = Application.objects.filter(student=student,status="rejected").count()
    pending = Application.objects.filter(student=student,status="pending").count()

    return Response({"total_applications":applications,
                     "selected":selected,
                     "rejected":rejected,
                     "pending":pending})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recruiter_dashboard(request):
    recruiter = RecruiterProfile.objects.filter(user=request.user).first()
    if not recruiter:
        return Response({"error":"recruiter not found"})
    jobs = Job.objects.filter(recruiter=recruiter).count()
    if not jobs:
        return Response({
                        "total_jobs":0,
                        "total_applications":0,
                        "selected":0,
                        "rejected":0,
                        "pending":0
                        })
    applications = Application.objects.filter(job__recruiter=recruiter).count()
    if not applications:
        return Response({"total_applications":0,
                     "Selected":0,
                     "Rejected":0,
                     "Pending":0})
    selected = Application.objects.filter(job__recruiter=recruiter,status="Selected").count()
    rejected = Application.objects.filter(job__recruiter=recruiter,status="Rejected").count()
    pending = Application.objects.filter(job__recruiter=recruiter,status="Pending").count()

    return Response({"total_jobs":jobs,
                    "total_applications":applications,
                     "selected":selected,
                     "rejected":rejected,
                     "pending":pending})

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_job_details(request):
    job_id = request.data.get("job_id")
    job = Job.objects.filter(id=job_id).first()
    if not job:
        return Response({"error":"job does not exist"})
    serializer = JobSerializer(job,data=request.data,partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"successfully updated the job details"})
    return Response(serializer.errors)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_job(request):
    job_id = request.data.get("job_id")
    job = Job.objects.filter(id=job_id).first()
    if not job:
        return Response({"error":"job does not exist"})
    job.delete()
    return Response({"message":"successfully deleted the job"})

@api_view(["POSt"])
@permission_classes([IsAuthenticated])
def search_job(request):
    keyword = request.data.get("keyword")

    jobs = Job.objects.filter(
        Q(job_title__icontains=keyword)
        |
        Q(required_skills__icontains=keyword)
    )

    serializer = JobSerializer(
        jobs,
        many=True
    )

    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def job_filter(request):
    filters = {}
    location = request.data.get("location")
    job_type = request.data.get("job_type")
    experience_required = request.data.get("experience_required")

    if location:
        filters["location"] = location
    if job_type:
        filters["job_type"] = job_type
    if experience_required:
        filters["experience_required"] = experience_required

    jobs = Job.objects.filter(**filters)
    if not jobs:
        return Response({"message":"no jobs are there to show"})

    serializer = JobSerializer(jobs,many=True)

    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def withdraw_application(request):
    job_id = request.data.get("job_id")
    job = Job.objects.filter(id=job_id).first()
    if not job:
        return Response({"error":"job does not exist"})
    
    student = StudentProfile.objects.filter(user=request.user).first()
 
    application = Application.objects.filter(job=job,student=student).first()
    if not application:
        return Response({"error":"you did not applied to this job"})
    
    application.delete()
    return Response({"message":"application withdraw success"})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def recommend_jobs(request):
    student = StudentProfile.objects.filter(user=request.user).first()
    resume = student.resume
    resume_text = extract_resume_text(resume)
    resume_data = extract_resume_data(resume_text)

    jobs = Job.objects.all()
    jobs_data = []

    for job in jobs:
        jobs_data.append(
            {
                "job_id":job.id,
                "job_title":job.job_title,
                "required_skills":job.required_skills,
                "job_description":job.job_description
            }
        )
    prompt = f"""
you are an AI job recommendation system

student resume data:
{resume_data}
available jobs:
{jobs_data}
recommend the top 5 jobs that best match the candidate

return only JSON.
format:
{{
"recommand_jobs":[
    {{
        "job_id":"",
        "job_title":"",
        "match_score":"",
        "reason":""
    }}
    ]
}}
"""
    response = model.generate_content(prompt)
    response_text = response.text.strip()
    response_text = response_text.replace("```json","")
    response_text = response_text.replace("```","")
    recommendations = json.loads(response_text)
    return Response(recommendations)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_interview_questions(request):
    job_id = request.data.get("job_id")

    job = Job.objects.filter(id=job_id).first()

    if not job:
        return Response({"error":"job not found"})
    
    prompt = f"""
You are an expert technical interviewer.

Job Title:
{job.job_title}

Required Skills:
{job.required_skills}

Experience Required:
{job.experience_required}

Job Description:
{job.job_description}

Generate:

5 Easy MCQs
3 Medium MCQs
2 Hard MCQs

Each question must contain:

- difficulty
- question
- option_a
- option_b
- option_c
- option_d

Return ONLY JSON.

Format:

{{
    "questions":[
        {{
            "difficulty":"Easy",
            "question":"",
            "option_a":"",
            "option_b":"",
            "option_c":"",
            "option_d":"",

        }}
    ]
}}
"""
    response = model.generate_content(prompt)
    response_text = response.text.strip()
    response_text = response_text.replace("```json","")
    response_text = response_text.replace("```","")
    questions = json.loads(response_text)
    return Response(questions)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def evaluate_interview_test(request):

    job_id = request.data.get("job_id")

    job = Job.objects.filter(id=job_id).first()

    if not job:
        return Response({"error": "job not found"})

    responses = request.data.get("responses")

    prompt = f"""
You are an expert technical interviewer.

Job Title:
{job.job_title}

Required Skills:
{job.required_skills}

Experience Required:
{job.experience_required}

Job Description:
{job.job_description}

Candidate MCQ Responses:

{responses}

Evaluate the responses.

Determine which selected options are correct.

Provide:

1. Score out of 10
2. Percentage
3. Strong Areas
4. Weak Areas
5. Improvement Suggestions
6. Hiring Recommendation
7. Question Feedback

Return ONLY JSON.

Format:

{{
    "score":"",
    "percentage":"",
    "strong_areas":[],
    "weak_areas":[],
    "suggestions":[],
    "recommendation":"",
    "question_feedback":[
        {{
            "question":"",
            "selected_option":"",
            "result":"",
            "feedback":""
        }}
    ]
}}
"""

    response = model.generate_content(prompt)

    response_text = response.text.strip()

    response_text = response_text.replace(
        "```json",
        ""
    )

    response_text = response_text.replace(
        "```",
        ""
    )

    result = json.loads(response_text)

    return Response(result)