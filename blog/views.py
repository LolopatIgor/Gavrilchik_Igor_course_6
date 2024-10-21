from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from blog.models import Blog


class BlogDetailView(DetailView):
    model = Blog

    def get(self, request, *args, **kwargs):
        blog = self.get_object()
        blog.view_count += 1
        blog.save()
        return super().get(request, *args, **kwargs)
