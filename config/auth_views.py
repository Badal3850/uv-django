# accounts/views.py

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
from django.utils.translation import gettext as _
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

@require_POST
def ajax_login_view(request):
    login_input = request.POST.get('login', '').strip()
    password = request.POST.get('password', '').strip()

    # Determine if login is email or username
    try:
        validate_email(login_input)
        user = User.objects.filter(email__iexact=login_input).first()
        username = user.username if user else None
    except ValidationError:
        username = login_input

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return JsonResponse({'success': True, 'redirect_url': '/'})
    else:
        return JsonResponse({
            'success': False,
            'errors': {
                '__all__': [_("Invalid credentials. Please try again.")],
            }
        })
    
def logout_view(request):
    logout(request)
    return redirect('home')


@require_POST
def ajax_signup_view(request):
    email = request.POST.get('email', '').strip()
    username = request.POST.get('username', '').strip()
    password1 = request.POST.get('password1', '').strip()
    password2 = request.POST.get('password2', '').strip()

    errors = {}
    # if not username:
    #     if settings.ACCOUNT_USERNAME_REQUIRED:
    #         errors['username'] = _('Username is required.')
    #     else:

    # if User.objects.filter(username=username).exists():
    #     errors['username'] = _('This username is already taken.')

    if not email:
        errors['email'] = _('Email is required.')
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors['email'] = _('Enter a valid email address.')
        else:
            if User.objects.filter(email=email).exists():
                errors['email'] = _('This email is already in use.')

    if not password1 or not password2:
        errors['password1'] = _('Password is required.')
    elif password1 != password2:
        errors['password2'] = _('Passwords do not match.')

    if errors:
        return JsonResponse({'success': False, 'errors': format_form_errors(errors)})
    user = User.objects.create(
        username=email,
        email=email,
        password=make_password(password1),
    )
    login(request, user,backend='django.contrib.auth.backends.ModelBackend')
    return JsonResponse({'success': True, 'redirect_url': '/'})


@require_POST
def ajax_password_reset_view(request):
    email = request.POST.get('email', '').strip()
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'success': False, 'errors': {'email': _('Enter a valid email address.')}})

    user = User.objects.filter(email=email).first()

    if not user:
        return JsonResponse({'success': False, 'errors': {'email': _('No user found with this email address.')}})

    # Send dummy reset link (In production, generate a token-based link)
    send_mail(
        subject="Password Reset",
        message="Click the link to reset your password: https://example.com/reset-password/",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
    return JsonResponse({'success': True, 'message': _('Password reset link sent to your email.')})


@require_POST
def ajax_username_recovery_view(request):
    email = request.POST.get('email', '').strip()
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'success': False, 'errors': {'email': _('Enter a valid email address.')}})

    users = User.objects.filter(email=email)
    if not users.exists():
        return JsonResponse({'success': False, 'errors': {'email': _('No account found with this email.')}})

    usernames = [u.username for u in users]

    send_mail(
        subject='Your ToolVerse Username',
        message='Your username(s):\n' + "\n".join(usernames),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return JsonResponse({'success': True, 'message': _('Username has been sent to your email.')})

def format_form_errors(errors):
    formatted = {}

    if hasattr(errors, 'items'):
        # errors is a dict-like object (e.g., ValidationError.message_dict)
        for field, messages in errors.items():
            if isinstance(messages, (list, tuple)):
                formatted[field] = [str(m) for m in messages]
            else:
                formatted[field] = [str(messages)]
    else:
        # fallback for string-based errors
        formatted['__all__'] = [str(errors)]

    return formatted