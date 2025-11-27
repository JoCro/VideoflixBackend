from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from .serializers import RegisterSerializer, LoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from .services import send_activation_email, send_password_reset_email

User = get_user_model()


class RegisterView(APIView):
    """
    This view:
    -accepts registration data, validates it through the registration Serializer
    -creates an inactive user account and triggers the email activation process
    -returns basic user information after successful registration.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()

        token, uidb64, activation_link = send_activation_email(user, request)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "token": token,
                "activation_link": activation_link,
            },
            status=status.HTTP_201_CREATED,
        )


class ActivateAccountView(APIView):
    """
    this View activates the user account after the user clicked on the Link in the email (requires an valid token).
    """
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is None:
            return Response({"message": "Invalid or expired acitvation token."}, status=status.HTTP_400_BAD_REQUEST,)

        if user.is_active:
            return Response({"message": "Account already activated"}, status=status.HTTP_200_OK,)

        user.is_active = True
        user.save()

        return Response({"message": "Account successfully activated"}, status=status.HTTP_200_OK,)


class LoginView(APIView):
    """
    This view generates access- and refresh JWT tokens if a user tries to log-in with valid credentials. 
    The tokens will be stored in httponly cookies
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response(
            {
                "detail": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite='Lax',
            secure=False,
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            samesite='Lax',
            secure=False,
        )
        return response


class LogoutView(APIView):
    """
    POST /api/lgout/
    Blacklists the refresh-token and deletes the access and refresh tokens from cookies
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({'detail': 'Refresh token not provided.'}, status=status.HTTP_400_BAD_REQUEST,)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except (TokenError, InvalidToken):
            return Response({"detail": "Invalid or already expired token"}, status=status.HTTP_400_BAD_REQUEST,)
        response = Response(
            {"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid"}, status=status.HTTP_200_OK,)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class TokenRefreshView(APIView):
    """
    POST /api/token/refresh/
    Expects the refresh token in the httpOnly-cookie.
    Returns a new Access-Token an sets a new access_token cookie.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if refresh_token is None:
            return Response({"detail": "Refresh token not provided"}, status=status.HTTP_400_BAD_REQUEST,)
        try:
            refresh = RefreshToken(refresh_token)
        except (TokenError, InvalidToken):
            return Response({"detail": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED,)
        new_access = str(refresh.access_token)
        response = Response(
            {
                "detail": "Token refreshed",
                "access": new_access,
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key='access_token',
            value=new_access,
            httponly=True,
            samesite='Lax',
            secure=False,
        )
        return response


class PasswordResetRequestView(APIView):
    """
    POST /api/password_reset/
    Expects an email in the request data.
    Sends a password reset email if the user with the provided email exists.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.get_user()
        send_password_reset_email(user, request)
        return Response({"detail": "An email has been sent  to reset your password."}, status=status.HTTP_200_OK,)


class PasswordResetConfirmView(APIView):
    """
    POST /api/password_confirm/<uidb64>/<token>/
    Expects a new password and a confirm password in the request data.
    """

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is None:
            return Response({"detail": "Invalid password reset link."}, status=status.HTTP_400_BAD_REQUEST,)
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired password reset token"}, status=status.HTTP_400_BAD_REQUEST,)
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user)
        return Response({"detail": "Your Password has been successfully reset."}, status=status.HTTP_200_OK,)
