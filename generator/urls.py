"""
URL Configuration for AI Brief Generator

Requirements adherence:
- One endpoint for brief generation
- Clear URL routing structure
"""

from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    # Main application page
    path('', views.index, name='index'),
    
    # API endpoint for brief generation (the main requirement)
    path('api/generate-brief/', views.generate_brief, name='generate_brief'),
    
    # Health check endpoint
    path('api/health/', views.health_check, name='health_check'),

    # Testing utility to force provider changes
    path('api/testing/set-provider/', views.set_provider, name='set_provider'),
]
