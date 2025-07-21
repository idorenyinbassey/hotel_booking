from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(TemplateView):
    """
    View for the home page.
    """
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add featured hotels to context
        return context


class AboutView(TemplateView):
    """
    View for the about page.
    """
    template_name = 'core/about.html'


class ContactView(TemplateView):
    """
    View for the contact page.
    """
    template_name = 'core/contact.html'