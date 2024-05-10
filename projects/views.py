from os import read
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from regex import P
from MyTest.testcontext import test_contex
from django.shortcuts import render
from .forms import UserInputForm
from django_ratelimit.decorators import ratelimit

from users.models import UserBookData

from aifolder import BookDataApis, ChatGptCall, CreateUserReadingPersona
from .models import  Books, Comment, Vote
from .management.commands import getbook, get_upvoted_book, addbooks, check_books,  UpdateVoteCount
from .management.commands.GetUserData import UserDataGetter



def set_cookie(request):
    response = HttpResponse("Cookie has been set")
    response.set_cookie('example_cookie', 'example_value', max_age=3600)  # Cookie expires in 1 hour
    return response



def get_read_books(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'User not authenticated'}, status=401)


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

        return JsonResponse({'read_books': read_books_list}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def projects(request):
    print("home")
    
    read_books_list = []

    user_data_getter = UserDataGetter(request)

    if request.user.is_authenticated:
        up_voted_books = get_upvoted_book.get_upvoted_books_by_user(request.user)
        vote_count_data = user_data_getter.get_user_vote_count_data()
        print("PPPPPPPPPPPPPPPPPPPPPPPP")
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
    user_data_getter = UserDataGetter(request)
    context = []
    function_type = 1

   
            
    action = request.POST.get('action')
    print(action)
    if action == 'by_personality':
            function_type = 2
    if action == 'by_paragraph':
            function_type = 3
                
    print(function_type)
     
    if request.user.is_authenticated:
        upvoted_books = user_data_getter.get_user_vote_count_data()
    else:
        upvoted_books = []

    print(upvoted_books)

    if function_type == 1:
        # Get data from request.GET if using the GET method
        recent_reads = request.POST.get('recent_reads')
        desired_feeling = request.POST.get('desired_feeling')
        character_plot_preferences = request.POST.get('character_plot_preferences')
        pacing_narrative_style = request.POST.get('pacing_narrative_style')
        

        # Perform actions specific to function_type 1
        try:
            context = ChatGptCall.RecommendWithAnswers([recent_reads, desired_feeling, character_plot_preferences, pacing_narrative_style], upvoted_books)
        except Exception as e:
            print(f"Error occurred while generating context: {e}")
            context = []

    elif function_type == 2:
        data = user_data_getter.get_user_reading_persona()
        print("User data:",data)
        try:
            context = ChatGptCall.RecommendWithReadingPersona(data)
            print("Context:",context)
        except Exception as e:
            print(f"Error occurred while generating context: {e}")
            context = []
    elif function_type == 3:
        print("MAMAEAEMAMEMAMEMA")
        
    # Check if book is already exists in data base. If exists, filter on check_books function for avoid to unnecessary api calls
    filtered_books = check_books.remove_existing_books(context)
    
    if filtered_books: # if there is a not added or not got the data from api
        # Get filtered book's data for the first time
        print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTt")
        print(filtered_books)
        print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
        respond = BookDataApis.main(filtered_books)
        print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
        print(respond)
        # Add the filtered books to data base for the first time
        addbooks.add_books(respond)
    print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV")
    print(context)
    
    

    books = getbook.search_books_in_database(context)
    
    index = 0
    for book in books:
        explanation = context[index].get('explanation') if context[index] is not None else "No explanation available."
        book.explanation = explanation
        index += 1
    
    books_data = []
    for book in books:
    # Constructing a dictionary for each book with all the required details
        book_dict = {
            'name': book.name,
            'author': book.author,
            'cover_image_url': book.cover_image_url if hasattr(book, 'cover_image_url') else None,  #
            'explanation': book.explanation if hasattr(book, 'explanation') else "No explanation available.",
            'total_votes': book.total_votes if hasattr(book, 'total_votes') else 0, 
            'vote_ratio': book.vote_ratio if hasattr(book, 'vote_ratio') else "N/A",  
            'published_year': book.published_year if hasattr(book, 'published_year') else "Unknown",  
            'description': book.description if hasattr(book, 'description') else "Description not available.", 
            # 'amazon_id': book.amazon_id if hasattr(book, 'amazon_id') else 'N/A',
            'id': book.id,   
            'detail_url': reverse('book-detail', args=[str(book.id)])
        }
        books_data.append(book_dict)

    # Get user's read books
    read_books_list = []
    if request.user.is_authenticated:
        try:
            user_data_getter = UserDataGetter(request)
            read_books_context = user_data_getter.get_user_read_data()

            if read_books_context is not None:
                read_books = read_books_context['read_books']
                read_books_list = [{'name': book.name, 'author': book.author if book.author else 'Unknown'} for book in read_books] 
                
        except Exception as e:
            print(f"Error occurred while getting user's read books: {e}")
            return JsonResponse({'error': str(e)}, status=500)


    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    print(read_books_list)
    # Returning JSON response
    try:
        return JsonResponse({'books': books_data, 'read_books': read_books_list}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def vote(request, book_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to vote.")
    
    try:
        book = get_object_or_404(Books, id=book_id)
        vote_type = request.POST.get('vote')
        
        current_vote = Vote.objects.filter(user=request.user, book=book).first()
        if book.vote_total is None:
            book.vote_total = 0
            book.upvotes_count = 0
        if current_vote:
            # If the user is submitting the same vote, it's considered a retraction
            if current_vote.vote_type == vote_type:
                current_vote.delete()
                if vote_type == 'up':
                    book.vote_total -= 1
                    UpdateVoteCount.decrease_vote_count(request)
                    if book.upvotes_count is not None:
                        book.upvotes_count -= 1
                else:
                    book.vote_total += 1
            else:
                # Change the vote and adjust book vote_total accordingly
                current_vote.vote_type = vote_type
                current_vote.save()
                if vote_type == 'up':
                    book.vote_total += 2  # One to cancel out the downvote, one to add the upvote
                    if book.upvotes_count is not None:
                        book.upvotes_count += 1
                    UpdateVoteCount.increase_vote_count(request)
                else:
                    book.vote_total -= 2  # One to cancel out the upvote, one to add the downvote
                    if book.upvotes_count is not None:
                        book.upvotes_count -= 1
                    UpdateVoteCount.decrease_vote_count(request)
        else:
            # If no current vote, create a new one and adjust book vote_total
            Vote.objects.create(user=request.user, book=book, vote_type=vote_type)
            if vote_type == 'up':
                book.vote_total += 1
                if book.upvotes_count is not None:
                    book.upvotes_count += 1
                UpdateVoteCount.increase_vote_count(request)
            else:
                book.vote_total -= 1
                UpdateVoteCount.decrease_vote_count(request)
        book.save()
        
        # Calculate the ratio
        upvotes_count = book.upvotes_count
        total_votes_count = abs(book.vote_total)
        

        if total_votes_count > 0 and upvotes_count is not None:
            book.vote_ratio = int((upvotes_count / total_votes_count) * 100)
        else:
            book.vote_ratio = 0

        book.save()
        
        return JsonResponse({
            'vote_total': book.vote_total,
            'vote_ratio': book.vote_ratio
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




@login_required
def post_comment(request, book_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to post a comment.")
    
    if request.method == 'POST':
        try:
            comment_text = request.POST.get('comment', '')  # Get the comment text or default to empty string
            book = get_object_or_404(Books, id=book_id)  # Get the book object or return 404 if not found

            # Create a new comment instance
            comment = Comment(
                book=book,
                body=comment_text,  # Use the comment text from the form
                created=timezone.now(),  # Set the created time to now
                user=request.user  # Assign the logged-in user to the comment
            )

            # Save the comment to the database
            comment.save()

            # Redirect back to the book detail page
            return redirect('book-detail', book_id=book_id)  
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # If not a POST request, return a bad request response
        return HttpResponseBadRequest("Invalid request method.")

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