from django.urls import path
from .views import *

urlpatterns = [
    path("Student_Signup/",Student_Signup),
    path("Recruiter_Signup/",Recruiter_Signup),
    path("Company_Signup/",Company_Signup),
    path("analyze_resume/",analyze_resume),
    path("Create_Job/",Create_Job),
    path("apply_job/",apply_job),
    path("view_applied_jobs/",view_applied_jobs),
    path("view_applicants/",view_applicants),
    path("manage_application_status/",manage_application_status),
    path("student_dashboard/",student_dashboard),
    path("recruiter_dashboard/",recruiter_dashboard),
    path("update_job_details/",update_job_details),
    path("delete_job/",delete_job),
    path("search_job/",search_job),
    path("job_filter/",job_filter),
    path("withdraw_application/",withdraw_application),
    path("recommend_jobs/",recommend_jobs),
    path("generate_interview_questions/",generate_interview_questions),
    path("evaluate_interview_test/",evaluate_interview_test),
    path("view_jobs/",view_jobs),
    
]
