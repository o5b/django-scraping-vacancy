from django.views import generic

from . import models


class IndexView(generic.TemplateView):
    template_name = 'main/index.html'


class AboutView(generic.TemplateView):
    template_name = 'main/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = models.About.objects.first()
        return context
