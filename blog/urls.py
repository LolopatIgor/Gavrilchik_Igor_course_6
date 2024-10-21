from django.urls import path
from django.views.decorators.cache import cache_page

from blog.apps import BlogConfig
from blog.views import BlogDetailView

app_name = BlogConfig.name
#test
urlpatterns = [
    path('view/<slug:slug>/', cache_page(120)(BlogDetailView.as_view()), name='view'),
]
