from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('create_todo/', views.TodoCreate.as_view()),
    path('update_todo/<int:pk>/', views.TodoUpdate.as_view()),
]

