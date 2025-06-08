from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/summarize/', views.summarize_review),
]