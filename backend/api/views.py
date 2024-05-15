from django.shortcuts import render
from django.http import HttpResponse
from .models import Profile
from rest_framework import viewsets
# from .serializers import ProfileSerializer

def home(request):
    return HttpResponse("Hello")