from turtle import update
from venv import logger
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.urls import reverse
from django.utils import timezone

from .management import AddBooks, GetBook, GetUpvotedBooks
from .management import CheckBooks
from aifolder import BookDataApis, ChatGptCall, CreateUserReadingPersona
from .management.GetUserData import UserDataGetter
from .management import UpdateVoteCount
from django.shortcuts import get_object_or_404, redirect
from .models import Books, Vote, Comment

class BookService:

    def __init__(self, request):
        self.request = request
        self.user_data_getter = UserDataGetter(request)
        self.is_authenticated = request.user.is_authenticated

    def get_function_type(self, action):
        if action == 'by_personality':
            print("SELECTED 2")
            return 2
        if action == 'by_paragraph':
            print("SELECTED 3")
            return 3
        if action == 'by_answers':
            print("SELECTED 1")
            return 1

    

    def get_context_based_on_function_type(self, function_type):
        print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFunction type:", function_type)
        upvoted_books = []
        if function_type == 1:
            recent_reads = self.request.POST.get('recent_reads')
            desired_feeling = self.request.POST.get('desired_feeling')
            character_plot_preferences = self.request.POST.get('character_plot_preferences')
            pacing_narrative_style = self.request.POST.get('pacing_narrative_style')
            print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
            print(f"User answers: {recent_reads}, {desired_feeling}, {character_plot_preferences}, {pacing_narrative_style}")

            if self.is_authenticated:
                upvoted_books = GetUpvotedBooks.get_upvoted_books_by_user(self.request.user)
                return ChatGptCall.RecommendWithAnswers([recent_reads, desired_feeling, character_plot_preferences, pacing_narrative_style], upvoted_books)
            return ChatGptCall.RecommendWithAnswers([recent_reads, desired_feeling, character_plot_preferences, pacing_narrative_style], upvoted_books)
        
        elif function_type == 2:
            
            data = self.user_data_getter.get_user_reading_persona()
            print("XXXXXXXXXXXXXXXXXXXXXX")
            print(data)

            return ChatGptCall.RecommendWithReadingPersona(data)
        elif function_type == 3:
            data = self.request.POST.get('self_description')
            logger.info(f"User self description: {data}")

            return ChatGptCall.RecommendWithParagraph(data)
        return []

    def filter_and_add_books(self, context):
        filtered_books = CheckBooks.remove_existing_books(context)
        if filtered_books:
            respond = BookDataApis.main(filtered_books)
            AddBooks.add_books(respond)
        return context

    def get_books_with_explanations(self, context):
        books = GetBook.search_books_in_database(context)
        for index, book in enumerate(books):
            explanation = context[index].get('explanation') if context[index] is not None else "No explanation available."
            book.explanation = explanation
        return books

    def format_books_data(self, books):
        books_data = []
        for book in books:
            book_dict = {
                'name': book.name,
                'author': book.author,
                'cover_image_url': book.cover_image_url if hasattr(book, 'cover_image_url') else None,
                'explanation': book.explanation if hasattr(book, 'explanation') else "No explanation available.",
                'total_votes': book.total_votes if hasattr(book, 'total_votes') else 0,
                'vote_ratio': book.vote_ratio if hasattr(book, 'vote_ratio') else "N/A",
                'published_year': book.published_year if hasattr(book, 'published_year') else "Unknown",
                'description': book.description if hasattr(book, 'description') else "Description not available.",
                'categories': book.categories if hasattr(book, 'categories') else "No categories available.",
                'id': book.id,
                'detail_url': reverse('book-detail', args=[str(book.id)])
            }
            books_data.append(book_dict)
            
        return books_data

    def update_recommended_count(self, books):
        for book in books:
            book_id = book.get('id')
            if book_id:
                book_obj = get_object_or_404(Books, id=book_id)
                if book_obj.recommended_count is not None:
                    book_obj.recommended_count += 1
                book_obj.save()
        
        
        
    def get_read_books_list(self):
        if not self.is_authenticated:
            return []
        read_books_context = self.user_data_getter.get_user_read_data()
        if read_books_context:
            read_books = read_books_context['read_books']
            return [{'name': book.name, 'author': book.author if book.author else 'Unknown'} for book in read_books]
        return []
    

    def vote(self, book_id):
        if not self.is_authenticated:
            return HttpResponseForbidden("You must be logged in to vote.")
        
        try:
            book = get_object_or_404(Books, id=book_id)
            vote_type = self.request.POST.get('vote')
            
            current_vote = Vote.objects.filter(user=self.request.user, book=book).first()
            if book.vote_total is None:
                book.vote_total = 0
                book.upvotes_count = 0
            if current_vote:
                # If the user is submitting the same vote, it's considered a retraction
                if current_vote.vote_type == vote_type:
                    current_vote.delete()
                    if vote_type == 'up':
                        book.vote_total -= 1
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
                        UpdateVoteCount.increase_vote_count(self.request)
                    else:
                        book.vote_total -= 2  # One to cancel out the upvote, one to add the downvote
                        if book.upvotes_count is not None:
                            book.upvotes_count -= 1
                        UpdateVoteCount.decrease_vote_count(self.request)
            else:
                # If no current vote, create a new one and adjust book vote_total
                Vote.objects.create(user=self.request.user, book=book, vote_type=vote_type)
                if vote_type == 'up':
                    book.vote_total += 1
                    if book.upvotes_count is not None:
                        book.upvotes_count += 1
                    UpdateVoteCount.increase_vote_count(self.request)
                else:
                    book.vote_total -= 1

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
        
    def post_comment(self, book_id):
        if not self.is_authenticated:
            return HttpResponseForbidden("You must be logged in to post a comment.")
        
        if self.request.method == 'POST':
            try:
                comment_text = self.request.POST.get('comment', '')  # Get the comment text or default to empty string
                book = get_object_or_404(Books, id=book_id)  # Get the book object or return 404 if not found

                # Create a new comment instance
                comment = Comment(
                    book=book,
                    body=comment_text,  # Use the comment text from the form
                    created=timezone.now(),  # Set the created time to now
                    user=self.request.user  # Assign the logged-in user to the comment
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
       