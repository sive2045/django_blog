from django.urls import path
from . import views

app_name = 'todo'
urlpatterns = [
    path('', views.index),
    path('list/',views.TodoList.as_view()),
    path('create_todo/', views.TodoCreate.as_view()),
    path('update_todo/<int:pk>/', views.TodoUpdate.as_view()),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('event/new/', views.event, name='event_new'),
    path('event/edit/<int:event_id>',views.event, name='event_edit')
]

