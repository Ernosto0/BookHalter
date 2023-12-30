from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from aifolder import ai
from .models import Project, Books, Comment
from .management.commands import getbook
def projects(request):
    
    projects = Project.objects.all()
    tags = Project.objects.values('tags').distinct()
    return render(request,'projects/projects.html')

# def get_result(request):
#     respond = ai.gpt_main()
#     return JsonResponse({'result':respond}, safe=False)

def project(request, pk):
    hello = "hello"
    return render(request,'projects/single-project.html',{'hello': hello})

def book_detail(request, book_id):
    book = get_object_or_404(Books, pk=book_id)
    context = {
        'book': book
    }
    return render(request, 'projects/book_detail.html', context)


def recommended_books(request):
    books = []
    context = []    
    user_query = request.GET.get('user_query')
    print(user_query)
    context = ai.gpt_main(user_query)
    books = getbook.search_books_in_database(context)
    html = render(request, 'projects/recommended_books.html', {'books': books})
    return HttpResponse(html, content_type='text/html')


# @login_required
def vote(request, book_id):
    bookid = get_object_or_404(Books, id=book_id)
    vote = request.POST.get('vote')
    
    book = Books.objects.get(pk=bookid)
    if book.vote_total is None:
        book.vote_total = 0
    
    if vote == 'up':
        book.vote_total +=  1
    else:
        book.vote_total -= 1
    total_books = book.objects.count()
    if total_books > 0:
        book.vote_ratio = int((book.vote_total / total_books) * 100)
    else:
        book.vote_ratio = 0

    book.save()
    
    return JsonResponse({
        'vote_total': book.vote_total,
        'vote_ratio': book.vote_ratio
    })


# @login_required
def post_comment(request, book_id):
    if request.method == 'POST':
        comment_text = request.POST.get('comment', '')  # Safely get the comment text or default to empty string
        book = get_object_or_404(Books, id=book_id)  # Get the book object or return 404 if not found

        # Create a new comment instance
        comment = Comment(
            book=book,
            body=comment_text,  # Assuming 'body' is the field for the comment text
            comment_text='up',  # Assuming you want a default vote type, change as needed
            created=timezone.now(),  # Set the created time to now
        )

        # Check if the user is authenticated, if so, assign the user to the comment
        if request.user.is_authenticated:
            comment.user = request.user

        # Save the comment to the database
        comment.save()

        # Redirect back to the book detail page
        return redirect('book-detail', book_id=book_id)
    else:
        # If not a POST request, return a bad request response
        return HttpResponse(status=400)