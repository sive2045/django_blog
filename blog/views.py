from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.text import slugify
from .models import Category, Post, Tag
from django.core.exceptions import PermissionDenied

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
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip() # strip() 공백 제거 

                tags_str = tags_str.replace(',',';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)

            return response
        else:
            return redirect('/blog/')

class PostUpdate(LoginRequiredMixin, UpdateView):
    """
    수정 되는 메커니즘 이해하기.
    """
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'tags']

    template_name = 'blog/post_update_form.html' # 경로지정, 미지정시 모델이름_form.html로 감.

    def dispatch(self, request, *args, **kwargs):
        """
        오버라이딩
        유저가 일치해야 수정 가능함
        """
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied

def category_page(request, slug):
    """
    slug 데이터는 front에서 입력받아, url.py에서 넘겨 받음
    no_category 와 같은 경우 프론트에서 새로 정의한 slug임
    그 외에는 PostList에서 정의함
    """
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