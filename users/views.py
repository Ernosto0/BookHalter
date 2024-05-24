from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import logging

from users.models import UserBookData
from .forms import RegistrationForm




logger = logging.getLogger(__name__)

class MyLoginView(LoginView):
    template_name = 'users/login.html'



def profiles(request):
    return render(request, 'users/profiles.html')

@require_POST
@csrf_exempt  # Use with caution, better to handle CSRF properly
def register(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        logger.debug('AJAX request received')  # Log AJAX request
        try:
            form = RegistrationForm(request.POST)
            if form.is_valid():
                form.save()
                logger.debug('Form is valid and saved')  # Log successful save
                return JsonResponse({'success': True})
            else:
                errors = {field: [str(error) for error in error_list] for field, error_list in form.errors.items()}
                logger.error(f"Form errors: {errors}")  # Log form errors
                return JsonResponse({'success': False, 'error': errors})
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")  # Log unexpected errors
            logger.error(f"Request data: {request.POST}")  # Log the request data for debugging
            return JsonResponse({'success': False, 'error': 'An unexpected error occurred.'})
    else:
        logger.error('Request is not AJAX')  # Log if the request is not AJAX
    return JsonResponse({'success': False, 'error': 'Invalid request'})
# Set up logging

@require_POST
@csrf_exempt  # Use with caution, better to handle CSRF properly
def ajax_login(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me') == 'on'
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks in seconds
            else:
                request.session.set_expiry(0)  # Browser session

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid username or password'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
