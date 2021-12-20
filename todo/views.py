from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic import DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.utils.safestring import mark_safe
from django.views import generic
from datetime import datetime, timedelta, date
from django.http import HttpResponse, HttpResponseRedirect
import calendar

from .models import *
from .utils import Calendar
from .forms import EventForm

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

class CalendarView(generic.ListView):
    model = Event
    template_name = 'todo/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        return context

def get_date(req_month):
    if req_month:
        year, month = (int(x) for x in req_month.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def event(request, event_id=None):
    instance = Event()
    if event_id:
        instance = get_object_or_404(Event, pk=event_id)
    else:
        instance = Event()

    form = EventForm(request.POST or None, instance=instance)
    if request.POST and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('todo:calendar'))
    return render(request, 'todo/event.html', {'form': form})