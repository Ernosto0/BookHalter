from django.core.exceptions import ObjectDoesNotExist
from projects.models import User

def GetUserData(request):
    current_user = request.user

    # Ensure the user is authenticated to avoid errors
    if not current_user.is_authenticated:
        # Handle the case where the user is not authenticated
        print("User is not authenticated.")
        return None  # Or return a suitable response/error message

    try:
        # Access the UserBookData related to the current user
        # This uses the 'related_name' set in the UserBookData model
        user_book_data = current_user.book_data

        # Now you can access user_reading_persona
        user_reading_persona = user_book_data.user_reading_persona

        # Do something with user_reading_persona
        # For example, return it
        return user_reading_persona

    except ObjectDoesNotExist:
        # Handle the case where UserBookData does not exist for the current user
        print("UserBookData does not exist for the current user.")
        return None  # Or return a suitable response/error message

    except Exception as e:
        # Handle other unforeseen errors
        print(f"An error occurred: {e}")
        return None  # Or return a suitable response/error message
