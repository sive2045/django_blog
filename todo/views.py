from django.shortcuts import redirect, render
from django.views.generic import DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from .models import Todo

def index(request):
    """
    main page update 예정
    """
    return render(
        request,
        'todo/base.html'
    )

class TodoCreate(LoginRequiredMixin, CreateView):
    model = Todo
    fields = ['title', 'content', 'deadline', 'is_complete', 'author']
    success_url = '/todo/'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    def form_vaild(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_staff):            
            form.instance.author = current_user           
            response = super(TodoCreate, self).form_valid(form)
            return response      
        else:
            return redirect('/todo/')        

class TodoUpdate(LoginRequiredMixin, UpdateView):
    model = Todo
    fields = ['title', 'content', 'deadline', 'is_complete']
    success_url = '/todo/'
    template_name = 'todo/todo_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(TodoUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied
    
    def form_valid(self, form):
        response = super(TodoUpdate, self).form_valid(form)
        return response