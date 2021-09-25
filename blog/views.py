from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Category, Post, Tag

class PostList(ListView):
    """
    post_list.html 필요
    """
    model = Post
    ordering = '-pk'

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context
        


class PostDetail(DetailView):
    """
    post_detail.html 필요
    """
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context

class  PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    post_form.html 필요
    author : 로그인 시 기입만 가능하므로 제외
    created_ad : 자동 기입
    tag : 추가적으로 포스트에 기입

    from_vaid() : CreateView의 매소드, 재정의해서 사용
    """
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self):
        """
        권한 인증 관련 
        장고에서 제공하는 함수?
        이를 통해 유저중 특정 권한 유저들만 페이지 접근가능하게 설정 가능
        """
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser): # 로그인 여부 조건문
            form.instance.author = current_user
            return super(PostCreate, self).form_valid(form)
        else:
            return redirect('/blog/')

def category_page(request, slug):
    if slug=='no_category': # no_category front에서 내가 지정한 slug임
        category='미분류'
        post_list = Post.objects.filter(category=None)
    else :
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list' : post_list,
            'categories' : Category.objects.all(),
            'no_category_post_count' : Post.objects.filter(category=None).count(),
            'category' : category,
        }
    )

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all() # 자식 모델을 사용할 때 쓰는 형식. [자식모델소문자]_set

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list' : post_list,
            'tag' : tag,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
        }
    )