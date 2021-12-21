from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown
from django.urls import reverse

class Todo(models.Model):
    title = models.CharField(max_length=30)
    content = MarkdownxField()
    deadline = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_complete = models.BooleanField(blank=True, null=True)

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'[{self.pk}] {self.title} :: {self.author}'
    
    def get_absolute_url(self):
        return f'/todo/{self.author}/{self.pk}/'

    def get_content_markdown(self):
        """
        마크다운으로 작성한 content를
        HTML로 변환해줌
        """
        return markdown(self.content)

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    @property
    def get_html_url(self):
        url = reverse('todo:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'