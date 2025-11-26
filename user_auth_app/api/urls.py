from django.contrib import admin
from django.urls import path, include
from .views import RegisterView, ActivateAccountView, LoginView, LogoutView, TokenRefreshView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/',
         ActivateAccountView.as_view(), name='activate-account'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('password_reset/', PasswordResetRequestView.as_view(),
         name='password-reset'),
    path('password_confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(), name='password-confirm'),
]
