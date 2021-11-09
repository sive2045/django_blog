from django.shortcuts import redirect, render
from django.views.generic import DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Todo

def index(request):
    """
    main page update 예정
    """
    return render(
        request,
        'todo/base.html'
    )

class TodoCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Todo
    fields = ['title', 'content', 'deadline', 'is_complete']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    def form_vaild(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_superuser or current_user.is_staff):
            form.instance.author = current_user
            response = super(TodoCreate,self).form_vaild(form)
            return response
        else:
            return redirect('/todo/')
