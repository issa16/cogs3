from django.urls import reverse_lazy
from django.views import generic

from .forms import CustomUserCreationForm


class Register(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'register.html'
