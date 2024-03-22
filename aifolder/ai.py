from os import read
import openai
import json
from aifolder.extract_book_data import extract_books_info
from projects.management.commands import addbooks, getbook

with open("C:/project_bookai/aifolder/openaikey.txt", 'r') as file:

    openai.api_key = file.read()
    
messages = [
    {
        "role": "system",
        "content": "You are an intelligent book suggester AI and you know about books. Your task is to suggest books "
                   "for the users based on their input. After providing book suggestions, craft a friendly and "
                   "informative response to the user, incorporating these suggestions. Your book recommendations "
                   "should be in the format: 'title by author'. Avoid suggesting the same author's books repeatedly. "
                   "Do not use quotation marks around book names, and do not use 'and' between book names. Each book "
                   "name should be followed by a period."
    }
]





def make_suggestion(data):

    preferences_summary = " ".join([f"{pref['question']} {pref['answer']}" for pref in data["questions"].values()])

    liked_books_summary = ", ".join(data["user_liked_books"])


    while True:
        one_message = f"""Please make 10 book suggestions based on the user's answers of the these questions: {preferences_summary} 
        and considering the user previously liked these books: {liked_books_summary}.Explain the each book why you suggested it with 30-15 words. Each book must be on this format: 'title by author: 
        explanation'. Dont add any extra text. just book name, author and explanations about why did you suggest that 
        book."""

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
        
    
        

def RecommendWithAnswers(user_queries, up_voted_books):
     
    user_preferences = {
        "questions": {
            "recent_reads": {
                "question": "What are some books or authors you've recently enjoyed, and what did you like about them?",
                "answer": user_queries[0]
            },
            "desired_feeling": {
                "question": "How do you want to feel while reading your next book, and are there any specific themes or "
                            "settings you're interested in?",
                "answer": user_queries[1]
            },
            "character_plot_preferences": {
                "question": "Do you prefer stories focused on strong character development, complex villains, "
                            "or thrilling adventures? Or something else?",
                "answer": user_queries[2]
            },
            "pacing_narrative_style": {
                "question": "Do you have a preference for fast-paced, action-packed stories, or do you enjoy slow-burn "
                            "narratives that take their time to unfold?",
                "answer": user_queries[3]
            }},
            "user_liked_books": up_voted_books
    }

    reply = make_suggestion(user_preferences)

    extracted_data = extract_books_info(reply)

    return extracted_data


def RecommendWithReadingPersona(data):
    pass
