from django.views.generic import ListView, DetailView
from .models import Category, Post

class PostList(ListView):
    model = Post
    ordering = '-pk'

    def get_context_data(self, **kwargs):
        """
        공부가 필요한 함수. 
        꼭 추가적으로 공부하기.
        """
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context
        


class PostDetail(DetailView):
    model = Post