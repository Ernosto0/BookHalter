from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from aifolder import ai
from .models import Project, Books
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

def vote(request):
    try:
        print("Vote function called")
        # rest of code
    except Exception as e:
        print("Error:", e)
    book_id = request.POST.get('book_id')
    vote = request.POST.get('vote')
    
    book = Books.objects.get(pk=book_id)
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