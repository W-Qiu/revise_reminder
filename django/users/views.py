from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse

from .models import CustomUser
from .forms import CustomUserCreationForm
from .forms import CustomUserLoginForm
from .forms import ProfileUpdateForm

class SignUpView(CreateView):
    def get(self, request, *args, **kwargs):
        context = {'form': CustomUserCreationForm()}
        return render(request, 'users/signup.html', context)

    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 
                            f'Account created!')
            return redirect('login')
        return HttpResponseNotFound('<h1>Error</h1>')

class LoginView(CreateView):
    def get(self, request, *args, **kwargs):
        context = {'form': CustomUserLoginForm()}
        return render(request, 'users/login.html', context)

    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            # messages.success(request, f'Logged in!')
            return redirect('home')
        messages.success(request, 
                            f'Wrong account or password')
        return render(request, 'users/login.html', {'form': CustomUserLoginForm()})

def LogoutView(request):
    logout(request)
    # messages.success(request, f'Logged out!')
    return redirect('home')

class ProfileView(LoginRequiredMixin, TemplateView):
    login_url = '/login/'
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        user = CustomUser.objects.get(id=user_id)
        p_form = ProfileUpdateForm(initial=
                        {'preset_target' : user.preset_target,
                         'revise_strategy' : user.revise_strategy})
        context['p_form'] = p_form
        return context
    # u_form = UserUpdateForm(request.POST, instance=request.user)
    # p_form = ProfileUpdateForm(request.POST, request.FILES,  instance=request.user.profile)

    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        user = CustomUser.objects.get(id=user_id)

        preset_target = request.POST['preset_target']
        revise_strategy = request.POST['revise_strategy']

        user.preset_target = preset_target
        user.revise_strategy = revise_strategy
        user.save()
        messages.success(request, 
                            f'Profile Updated!')
        return redirect('profile')

class PasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    login_url = '/login/'
    template_name = 'users/password_change.html'
    success_url = '/home/'