from .models import *
from rest_framework import serializers

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = "__all__"

class RecruiterProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruiterProfile
        fields = "__all__"

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"

class  ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model =  Application
        fields = "__all__"

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model =  Company
        fields = "__all__"