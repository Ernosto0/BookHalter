import openai
from users.models import UserBookData



with open("C:/project_bookai/aifolder/openaikey.txt", 'r') as file:

    openai.api_key = file.read()


def CreatePersonality(liked_books):
    messages = [ {
        
            "role": "system",
            "content": "You are an intelligent book suggester AI. Your task is to analyze users' liked books and "
                       "describe their reading personality in a paragraph. Make sure to provide diverse. "

        }]
    one_message = f"Analyze the following liked books and describe the user's reading personality: {liked_books}. Minimum: 100, maximum: 200 words."

    if one_message:
        messages.append(
            {"role": "user", "content": one_message},
        )
        chat = openai.chat.completions.create( # type: ignore
            model="gpt-4-0125-preview", messages=messages # type: ignore
        )
        print(chat)
        reply = chat.choices[0].message.content
    
    return reply





def update_user_reading_persona(request, new_reading_persona):
    # Access the current user from the request
    current_user = request.user

    # Retrieve the UserBookData instance related to the current user
    # If it doesn't exist, you could choose to create one
    user_book_data, created = UserBookData.objects.get_or_create(user=current_user)

    # Update the user_reading_persona field
    user_book_data.user_reading_persona = new_reading_persona

    # Save the changes to the database
    user_book_data.save()

def main(request, liked_books):

    update_user_reading_persona(request, CreatePersonality(liked_books))