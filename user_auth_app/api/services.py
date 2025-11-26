import base64
from pathlib import Path
from django.conf import settings
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator


def get_logo_base64() -> str:
    """
    Returns the base64 encoded string of the logo image.
    """

    logo_path = Path(settings.BASE_DIR) / 'static'/'videoflix_icon.png'

    try:
        with open(logo_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('ascii')
    except FileNotFoundError:
        return ''


def send_activation_email(user, request):
    """
    Creates an activation link and a token for the user and sends an activation email to the user's email address.
    It also returns the Token, uidb64 and Link.
    """
    frontend_url = 'http://127.0.0.1:5500'
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    activation_link = (
        f"{frontend_url}/pages/auth/activate.html"f"?uid={uidb64}&token={token}")

    logo_base64 = get_logo_base64()
    # logo_url = request.build_absolute_uri("user_auth_app/videoflix_icon.png")
    subject = 'Confirm your Email'
    html_message = render_to_string(
        'activation_email.html', {'activation_link': activation_link, "logo_base64": logo_base64, 'user': user})

    plain_message = (
        f"Bitte aktiviere deinen Account über folgenden Link:\n{activation_link}")

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL',
                           "no-reply@example.com"),
        recipient_list=[user.email],
        html_message=html_message,
    )

    return token, uidb64, activation_link


def send_password_reset_email(user, request):
    """
    Creates a password reset link and a token for the user and sends a mail to the user's email address.
    The Link points to the frontend and includes uid & token as query parameters. 
    """
    frontend_url = 'http://127.0.0.1:5500'

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_link = (f"{frontend_url}/pages/auth/confirm_password.html"
                  f"?uid={uidb64}&token={token}")

    logo_base64 = get_logo_base64()

    subject = 'Password Reset Request'
    plain_message = (
        f"Hello {user.username},\n\n"
        "We recently received a request to reset your password. If you made this request, please click on the following button\n\n"

        f"{reset_link}\n\n"
        "Please note that for security reasons, this link is only valid for 24 hours.\n\n"
        "If you did not request a password reset, please ignore this email.\n\n"
        "Best regards, \n"
        "Your Videoflix team!")

    html_message = render_to_string(
        "password_reset_email.html",
        {
            "reset_link": reset_link,
            "logo_base64": logo_base64,
            "user": user,
        },
    )

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL",
                           "no-reply@example.com"),
        recipient_list=[user.email],
        html_message=html_message,
    )
    return uidb64, token, reset_link
