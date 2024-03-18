from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from regex import P


from aifolder import ai, openlibrary
from .models import Project, Books, Comment, Vote
from .management.commands import getbook, get_upvoted_book
from .management.commands import addbooks
def projects(request):
    
    projects = Project.objects.all()
    tags = Project.objects.values('tags').distinct()
    return render(request,'projects/projects.html')


def project(request, pk):
    hello = "hello"
    return render(request,'projects/single-project.html',{'hello': hello})

def home(request):
    return render(request, 'projects.html')

def book_detail(request, book_id):
    book = get_object_or_404(Books, pk=book_id)
    context = {
        'book': book
    }
    return render(request, 'projects/book_detail.html', context)


def recommended_books(request):
    books = []
    context = []    
    upvoted_books = get_upvoted_book.get_upvoted_books_by_user(request.user)
    print(upvoted_books)

    recent_reads = request.GET.get('recent_reads')
    desired_feeling = request.GET.get('desired_feeling')
    character_plot_preferences = request.GET.get('character_plot_preferences')
    pacing_narrative_style = request.GET.get('pacing_narrative_style')

    context = ai.gpt_main([recent_reads, desired_feeling, character_plot_preferences, pacing_narrative_style], upvoted_books)

    


    respond = openlibrary.main(context)

    
    addbooks.add_books(respond)

    books = getbook.search_books_in_database(respond)
    explanations_by_gpt = {book['explanation']: {} for book in context}
    print("::::::::::::::::::::::::::::::::::::::::")
    print(books)

    index = 0
    for book in books:
        book.explanation = respond[index]['explanation']
        index = index + 1
    
    html = render(request, 'projects/recommended_books.html', {'books': books} )
    return HttpResponse(html, content_type='text/html')


# TODO: Fix the vote up, down system

@login_required
def vote(request, book_id):
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
                
            else:
                book.vote_total += 1
                
        else:
            # Change the vote and adjust book vote_total accordingly
            current_vote.vote_type = vote_type
            current_vote.save()
            if vote_type == 'up':
                book.vote_total += 2  # One to cancel out the downvote, one to add the upvote
            else:
                book.vote_total -= 2  # One to cancel out the upvote, one to add the downvote
    else:
        # If no current vote, create a new one and adjust book vote_total
        Vote.objects.create(user=request.user, book=book, vote_type=vote_type)
        if vote_type == 'up':
            book.vote_total += 1
        else:
            book.vote_total -= 1

    # TODO: Fix the calculute the ratio system
            
    # Calculate the ratio
            
    # upvotes_count = book.upvotes_count

    # total_votes_count = abs(book.vote_total)

    # if total_votes_count > 0:
    #     book.vote_ratio = int((upvotes_count / total_votes_count) * 100)
    # else:
    #     book.vote_ratio = 0

    #     book.save()
    
    return JsonResponse({
        'vote_total': book.vote_total,
        'vote_ratio': book.vote_ratio
    })


@login_required
def post_comment(request, book_id):
    if request.method == 'POST':
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
    else:
        # If not a POST request, return a bad request response
        return HttpResponse(status=400)