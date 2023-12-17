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

def book_detail(request, pk):
    book = get_object_or_404(Books, pk=pk)
    context = {
        'book': book
    }
    return render(request, 'projects/book_detail.html', context)


def recommended_books(request):
    context = ai.gpt_main()
    books = getbook.search_books_in_database(context)
    html = render(request, 'projects/recommended_books.html', {'books': books})
    return HttpResponse(html, content_type='text/html')