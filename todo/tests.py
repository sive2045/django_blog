from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from bs4 import BeautifulSoup

class TestTodo(TestCase):
    def setup(self):
        """
        사전 db 처리
        """
        self.client = Client()
        self.user_sive = User.objects.create_user(username="sive", password="asdfqwer1234")
        self.user_sive.is_staff = True
        self.user_sive.save()

