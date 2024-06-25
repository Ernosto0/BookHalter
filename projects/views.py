import re
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from .management import GetUpvotedBooks, UpdateVoteCount
from users.models import UserBookData
from aifolder import CreateUserReadingPersona
from .models import Books, Comment, Vote
from .management.GetUserData import UserDataGetter
from .utils import BookService
from MyTest import testcontext
from django.core.cache import cache
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def get_read_books(request):
    print("get_read_books")
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False, 'error': 'User not authenticated'}, status=401)

    try:
        user_data_getter = UserDataGetter(request)
        read_books_context = user_data_getter.get_user_read_data()

        if read_books_context is not None:
            read_books = read_books_context['read_books']
            read_books_list = [{
                'name': book.name,
                'author': book.author if book.author else 'Unknown',
                'url': reverse('book-detail', args=[book.id])  # Adding URL for each book
            } for book in read_books]
        else:
            read_books_list = []

        return JsonResponse({'authenticated': True, 'read_books': read_books_list}, safe=False)
    except Exception as e:
        return JsonResponse({'authenticated': True, 'error': str(e)}, status=500)



def projects(request):
    logger.info("Home view called")
    
    read_books_list = []

    user_data_getter = UserDataGetter(request)

    if request.user.is_authenticated:
        up_voted_books = GetUpvotedBooks.get_upvoted_books_by_user(request.user)
        vote_count_data = user_data_getter.get_user_vote_count_data()
        
        print(up_voted_books)

    
        if len(up_voted_books) >= 20 and vote_count_data==20:
            # If there are more than 20 books; after voted an other 20 books, get last 20 and create an otr.
            UpdateVoteCount.reset_user_vote_count(request)
            print(up_voted_books)
            CreateUserReadingPersona.main(request, up_voted_books)
    
       


    return render(request,'projects/projects.html')

# def home(request):

#     return render(request, 'projects.html')

def book_detail(request, book_id):
    book = get_object_or_404(Books, pk=book_id)
    user = request.user


    is_read = False

    # Ensure the user has associated UserBookData
    if hasattr(user, 'book_data'):
        # Check if the book is in the user's read_books
        is_read = book in user.book_data.read_books.all()
    else:
        is_read = False

    context = {
        'book': book,
        'is_read': is_read
    }
    return render(request, 'projects/book_detail.html', context)


def get_cached_books(request):

    logger.info("get_cached_books view called")
    cache_key = 'recommended_books_cache'
    cached_data = cache.get(cache_key)

    if cached_data:
        logger.info("Returning cached data")
        return JsonResponse(cached_data, safe=False)
    else:
        logger.info("No cached data found")
        return JsonResponse({'books': [], 'read_books': []}, safe=False)


@csrf_exempt
@ratelimit(key='ip', rate='1/h', method='ALL', block=True)
def recommended_books(request):
    print("recommended_books")
    if request.method == 'POST':
        book_service = BookService(request)
        action = request.POST.get('action')
        function_type = book_service.get_function_type(action)
        print("function_type", function_type)
        
      

        try:
            book_service = BookService(request)
            action = request.POST.get('action')
            function_type = book_service.get_function_type(action)
            context = book_service.get_context_based_on_function_type(function_type)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        try:
            context = book_service.filter_and_add_books(context)
            books = book_service.get_books_with_explanations(context)
            books_data = book_service.format_books_data(books)
            read_books_list = book_service.get_read_books_list()

            response_data = {'books': books_data, 'read_books': read_books_list}
            cache.set('recommended_books_cache', response_data, timeout=1200) # Cache the response for 20 minutes

            return JsonResponse(response_data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
@login_required
def quickrecommended_books(request):
    print("quickrecommended_books")
    if request.method == 'POST':
        book_service = BookService(request)
        action = request.POST.get('action')
        function_type = book_service.get_function_type(action)
        print("function_type", function_type)

      

        try:
            book_service = BookService(request)
            action = request.POST.get('action')
            function_type = book_service.get_function_type(action)
            context = book_service.get_context_based_on_function_type(function_type)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        try:
            context = book_service.filter_and_add_books(context)
            books = book_service.get_books_with_explanations(context)
            books_data = book_service.format_books_data(books)
            read_books_list = book_service.get_read_books_list()

            response_data = {'books': books_data, 'read_books': read_books_list}
            cache.set('recommended_books_cache', response_data, timeout=1200) # Cache the response for 20 minutes

            return JsonResponse(response_data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def vote(request, book_id):
    book_service = BookService(request)
    return book_service.vote(book_id)

@login_required
def post_comment(request, book_id):
    book_service = BookService(request)
    return book_service.post_comment(book_id)

# Toggle the read status of books
@login_required
def toggle_read_status(request, book_id):
    print("toggle_read_status")
    if request.method == 'POST':
        book = get_object_or_404(Books, id=book_id)
        user_book_data, _ = UserBookData.objects.get_or_create(user=request.user)

        if book in user_book_data.read_books.all():
            user_book_data.read_books.remove(book)  # Remove the book if it's already read
            message = 'Book removed from your read list'
            print(message)
        else:
            user_book_data.read_books.add(book)  # Add the book if it's not in the read list
            message = 'Book marked as read'
            print(message)

        return JsonResponse({'status': 'success', 'message': message, 'read': book in user_book_data.read_books.all()})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    
@login_required
def check_authentication(request):
    return JsonResponse({'is_authenticated': request.user.is_authenticated})