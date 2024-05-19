from django.shortcuts import render
from django.http import HttpResponse
from .models import Profile
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ProfileSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

def home(request):
    return HttpResponse(f"Hello")