from django.core.exceptions import ObjectDoesNotExist
from projects.models import User
from users.models import UserBookData

class UserDataGetter:
    def __init__(self, request):
        self.request = request
        self.current_user = request.user

    def get_user_reading_persona(self):
        if not self.current_user.is_authenticated:
            print("User is not authenticated.")
            return None

        try:
            user_reading_persona = self.current_user.book_data.user_reading_persona
            return user_reading_persona

        except UserBookData.DoesNotExist:
            print("UserBookData does not exist for the current user.")
            return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_user_vote_count_data(self):
        if not self.current_user.is_authenticated:
            print("User is not authenticated.")
            return None

        try:
            user_vote_count_data = self.current_user.book_data.vote_count
            return user_vote_count_data

        except UserBookData.DoesNotExist:
            print("UserBookData does not exist for the current user.")
            return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_user_read_data(self):
        if not self.current_user.is_authenticated:
            print("User is not authenticated.")
            return None

        try:
            context = {}
            user_book_data = UserBookData.objects.get(user=self.current_user)
            read_books = user_book_data.read_books.all()
            print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
            for book in read_books:
                
                print(book.name)
            context['read_books'] = read_books
            print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
            print(context)
            print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
            return context

        except UserBookData.DoesNotExist:
            print("UserBookData does not exist for the current user.")
            return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
