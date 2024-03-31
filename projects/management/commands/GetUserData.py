from django.core.exceptions import ObjectDoesNotExist
from projects.models import User
from users.models import UserBookData

def GetUserData(request, data):
    current_user = request.user

    # Ensure the user is authenticated to avoid errors
    if not current_user.is_authenticated:
        print("User is not authenticated.")
        return None  # Or return a suitable response/error message

    if data == "user_reading_persona":
        try:
            # Access the UserBookData related to the current user using the 'related_name'
           # This directly accesses the related UserBookData instance

            

            # Now you can access user_reading_persona
            user_reading_persona = current_user.book_data.user_reading_persona
           

            return user_reading_persona

        except UserBookData.DoesNotExist:  # This is the more specific exception for when the related object does not exist
            print("UserBookData does not exist for the current user.")
            return None  # Or return a suitable response/error message

        except Exception as e:  # Catch other unforeseen errors
            print(f"An error occurred: {e}")
            return None  # Or return a suitable response/error message

    if data == "User_vote_count_data":
        try:
            user_vote_count_data = current_user.book_data.vote_count
            return user_vote_count_data
        
        except UserBookData.DoesNotExist:  # This is the more specific exception for when the related object does not exist
            print("UserBookData does not exist for the current user.")
            return None  # Or return a suitable response/error message

        except Exception as e:  # Catch other unforeseen errors
            print(f"An error occurred: {e}")
            return None  # Or return a suitable response/error message 

        
