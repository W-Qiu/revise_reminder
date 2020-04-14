"""revise_reminder URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.views.generic import TemplateView
import django.contrib.auth.views as auth_views

from users import views as users_views
from vocabularies import views as vocab_views
from word_logs import views as wl_views

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', vocab_views.direct, name='index'),
    path('home/', vocab_views.HomeView.as_view(), name='home'),
    path('yes/', vocab_views.YesView.as_view(), name='yes'),
    path('no/', vocab_views.NoView.as_view(), name='no'),
    path('new_word/', vocab_views.NewWordView.as_view(), name='new_word'),
    path('delete_word/', vocab_views.DeleteWordView.as_view(), name='delete_word'),
    path('all_user_words/', vocab_views.AllWordsView.as_view(),
         name='all_user_words'),
    path('single_word/', vocab_views.SingleWordView.as_view()),
    path('search/', vocab_views.SearchWordView.as_view(), name='search'),
    # path('word_images/', vocab_views.WordImagesView.as_view()),
    path('word_logs/', wl_views.AddWordLog.as_view(), name='word_logs'),
    path('signup/', users_views.SignUpView.as_view(), name='signup'),
    path('login/', users_views.LoginView.as_view(), name='login'),
    path('logout/', users_views.LogoutView, name='logout'),
    path('profile/', users_views.ProfileView.as_view(), name='profile'),
    path('password-change/', users_views.PasswordChangeView.as_view(),
         name='password_change'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]
