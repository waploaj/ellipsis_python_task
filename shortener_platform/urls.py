from django.urls import path

from shortener_platform.views import Index, DashboardView, NewLinkView, LinkView, EditLinkView, PasswordResetView, ProfileView, EditProfileView

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('home/', DashboardView.as_view(), name='home'),
    path('links/', LinkView.as_view(), name='links'),
    path('links/new/', NewLinkView.as_view(), name='new-link'),
    path('links/edit/<link>/', EditLinkView.as_view(), name='edit-link'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', EditProfileView.as_view(), name='edit-profile'),
    path('password/reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password/reset/confirm/', PasswordResetView.as_view(), name='password-reset-confirm'),
    path('password/set-password/', PasswordResetView.as_view(), name='set-password'),
]
