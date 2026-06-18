from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    resume = models.FileField()

class Company(models.Model):
    company_name = models.CharField(max_length=100)
    company_email = models.EmailField(max_length=100)
    company_website = models.URLField(max_length=200)
    company_description = models.TextField(max_length=500)
    company_location = models.TextField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

class RecruiterProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    desigination = models.CharField(max_length=100)
    company = models.ForeignKey(Company,on_delete=models.CASCADE)

class Job(models.Model):
    job_title = models.CharField(max_length=100)
    job_description = models.CharField(max_length=200)
    required_skills = models.CharField(max_length=100)
    salary = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=100)
    experience_required = models.CharField(max_length=20)
    deadline = models.DateField()
    company = models.ForeignKey(Company,on_delete=models.CASCADE)
    recruiter = models.ForeignKey(RecruiterProfile,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Application(models.Model):
    student = models.ForeignKey(StudentProfile,on_delete=models.CASCADE)
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    ats_score = models.IntegerField()
    status = models.CharField(max_length=50)
    applied_at = models.DateTimeField(auto_now_add=True)

