from django.urls import reverse
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required 
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit
from users.models import UserBookData
from aifolder import CreateUserReadingPersona
from .models import Books, Comment, Vote
from .management.commands import CheckBooks, GetUpvotedBooks, GetBook, AddBooks, UpdateVoteCount
from .management.commands.GetUserData import UserDataGetter
from .utils import BookService


def set_cookie(request):
    response = HttpResponse("Cookie has been set")
    response.set_cookie('example_cookie', 'example_value', max_age=3600)  # Cookie expires in 1 hour
    return response

def get_read_books(request):
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
    print("home")
    
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
    
        read_books = user_data_getter.get_user_read_data()

        if read_books is not None:
            read_books_list = [{'name': book_name, 'author': 'Unknown'} for book_name in read_books]

        

    return render(request,'projects/projects.html', {"read_books": read_books_list})



def home(request):

    return render(request, 'projects.html')

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


@csrf_exempt
@ratelimit(key='ip', rate='1/h', method='ALL', block=True)
def recommended_books(request):
    book_service = BookService(request)
    action = request.POST.get('action')
    function_type = book_service.get_function_type(action)

    try:
        context = book_service.get_context_based_on_function_type(function_type)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    context = book_service.filter_and_add_books(context)
    
    books = book_service.get_books_with_explanations(context)
    books_data = book_service.format_books_data(books)
    read_books_list = book_service.get_read_books_list()
    
    return JsonResponse({'books': books_data, 'read_books': read_books_list}, safe=False)


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
    
