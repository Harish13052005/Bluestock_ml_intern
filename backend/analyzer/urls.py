from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("analyze/", views.analyze_companies, name="analyze_companies"),
    path("results/", views.list_analyses, name="list_analyses"),
]
