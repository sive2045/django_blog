from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from .models import Post, Category, Tag

class TestView(TestCase):
    def setUp(self):
        """
        테스트 하면서 미리 담을 요소를 설정하는 곳.
        보통 테스트 DB를 생성함.
        """
        self.client = Client()
        self.user_sive = User.objects.create_user(username="sive", password="asdfqwer12")
        self.user_value = User.objects.create_user(username="value", password="asdfqwer12")
        self.user_value.is_staff = True
        self.user_value.save()

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')        

        self.tag_python_kor = Tag.objects.create(name="파이썬 공부", slug="파이썬-공부")
        self.tag_ptyhon = Tag.objects.create(name='Python', slug='python')
        self.tag_hello = Tag.objects.create(name='hello', slug='hello')

        self.post_001 = Post.objects.create(
            title="첫번째 포스트입니다.",
            content="헬로우 월드!!",
            author=self.user_sive,
            category=self.category_music,
        )
        self.post_001.tags.add(self.tag_hello) # 다대다 구조이기에 따로 add함수로 추가함.

        self.post_002 = Post.objects.create(
            title="두번째 포스트입니다.",
            content="두두헬로우 월드!!",
            author=self.user_value,
            category=self.category_programming,
        )

        self.post_003 = Post.objects.create(
            title="3번째 포스트입니다.",
            content="카테고리가 없을 수 도 있죠.",
            author=self.user_value,
        )
        self.post_003.tags.add(self.tag_ptyhon)
        self.post_003.tags.add(self.tag_python_kor)
    
    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)


    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Do It Django')
        self.assertIn(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertIn(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertIn(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertIn(about_me_btn.attrs['href'], '/about_me/')

    def test_post_list(self):
        # 포스트가 있는 경우
        self.assertEqual(Post.objects.count(), 3)
        
        response = self.client.get('/blog/')        
        self.assertEqual(response.status_code, 200)        
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')
        
        self.navbar_test(soup)
        self.category_card_test(soup)
        
        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)
        
        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_ptyhon.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)
        
        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_ptyhon.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_ptyhon.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

        self.assertIn(self.user_sive.username.upper(), main_area.text)
        self.assertIn(self.user_value.username.upper(), main_area.text)

        # 포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):
        self.assertIn(self.post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.post_001.title, soup.title.text)
        
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_music.name, post_area.text)
        
        self.assertIn(self.user_sive.username.upper(), main_area.text)
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)
        self.assertNotIn(self.tag_ptyhon.name, post_area.text)
    
    def test_category_page(self):
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)
        
        self.assertIn(self.category_programming.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        # 비로그인시 접근 불가
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff가 아닌 일반 유저가 로그인을 한다
        self.client.login(username='sive', password='asdfqwer12')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff인 value가 로그인 한다
        self.client.login(username='value', password='asdfqwer12')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        self.client.post(
            '/blog/create_post/',
            {
                'title' : 'Post Form 만들기',
                'content' : "Post Form 페이지를 만듭니다.",
            }
        )
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, "value")
    
    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 로그인하지 않은 경우
        respones = self.client.get(update_post_url)
        self.assertNotEqual(respones.status_code, 200)

        # 로그인은 했지만 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_sive)
        self.client.login(
            username=self.user_sive.username,
            password='asdfqwer12'
        )
        respones = self.client.get(update_post_url)
        self.assertEqual(respones.status_code, 403)

        # 작성자와 로그인 유저가 일치하는 경우
        self.client.login(
            username=self.post_003.author.username,
            password='asdfqwer12'
        )
        respones = self.client.get(update_post_url)
        self.assertEqual(respones.status_code, 200)
        soup = BeautifulSoup(respones.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        respones = self.client.post(
            update_post_url,
            {
                'title' : '세 번째 포스트를 수정 했습니다.' ,
                'content' : "temp post!",
                'category' : self.category_music.pk # pk로 수정함!!
            },
            follow=True
        )
        soup = BeautifulSoup(respones.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트를 수정 했습니다.', main_area.text)
        self.assertIn('temp post!', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)