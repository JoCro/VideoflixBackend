from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """
    Serializer handling user registration.

    -validates user input during the registration process
    -ensures that passwords match
    -creates an user account that needs to be activated via email
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """
        Validates that the email address is not already associated with an existing user
        """
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                'An User with this email already exists.')
        return value

    def validate(self, attrs):
        """
        Validates password and password confirmation
        """
        password = attrs.get('password')
        confirmed_password = attrs.get('confirmed_password')

        if password != confirmed_password:
            raise serializers.ValidationError(
                {'confirmed_password': 'Passwords do not match.'})

        validate_password(password)
        return attrs

    def create(self, validated_data):
        """
        Creates a new incactive user. Account will be set to active, as soon as the user confirms the activation via email
        """
        email = validated_data['email']
        password = validated_data['password']

        user = User.objects.create_user(
            username=email, email=email, password=password,)
        user.is_active = False
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    This serializer h andles authentication by verifying that the provided email and password correspond to an existing user account. It ensures the account is active and attaches the authenticated user isntance to the validated data.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email is None or password is None:
            raise serializers.ValidationError(
                'Email and password are required.')
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError('Invalid Login credentials.')
        if not user.is_active:
            raise serializers.ValidationError('User account is not activated.')
        attrs['user'] = user
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Validates that the email-address belongs to an existing account
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "No user is associated with this email")
        return value

    def get_user(self):
        email = self.validated_data['email']
        return User.objects.get(email__iexact=email)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Ensures that the user provides the new password twice (confirmation)
    Once validated, the serializer can update the user's password via the save() method.
    """
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."})
        validate_password(new_password)
        return attrs

    def save(self, user):
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user
