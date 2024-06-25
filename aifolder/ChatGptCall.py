from os import read
import openai
import json
from aifolder.ExtractBookData import extract_books_info
from projects.management import AddBooks
from projects.management import GetBook
import logging

logger = logging.getLogger(__name__)

with open("C:/BookPalAi/aifolder/openaikey.txt", 'r') as file:

    openai.api_key = file.read()
    
messages = [
    {
        "role": "system",
        "content": "You are an intelligent book suggester AI and you know about books. Your task is to suggest books "
                   "for the users based on their input. After providing book suggestions, craft a friendly and "
                   "informative response to the user, incorporating these suggestions. Your book recommendations "
                   "should be in the format: 'title by author': explanation. Avoid suggesting the same author's books repeatedly. "
                   "Do not use quotation marks around book names, and do not use 'and' between book names. Each book "
                   "name should be followed by a period. Always answer in English"
    }
]



def make_suggestion(prompt):

    while True:
        one_message = prompt

        if one_message:
            messages.append(
                {"role": "user", "content": one_message},
            )
            chat = openai.chat.completions.create( # type: ignore
                model="gpt-4o-2024-05-13", messages=messages # type: ignore
            )
        print(chat)
        reply = chat.choices[0].message.content # type: ignore

        return reply
        
    
        

def RecommendWithAnswers(user_queries, upvoted_books):
    logger.info(f"RecommendWithAnswers called: {user_queries}")
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
            "user_liked_books": ""
    }
    preferences_summary = " ".join([f"{pref['question']} {pref['answer']}" for pref in user_preferences["questions"].values()])

    liked_books_summary = ", ".join(user_preferences["user_liked_books"])

    prompt = f"""Please make 10 book suggestions based on the user's answers of the these questions: {preferences_summary} 
        and considering the user previously liked these books: {liked_books_summary}.Explain the each book why you suggested it with 20-30 words. Each book must be on this format: 'title by author: 
        explanation'. Dont add any extra text. just book name, author and explanations about why did you suggest that 
        book."""
    reply = make_suggestion(prompt)
    extracted_data = extract_books_info(reply)
    print(extracted_data)
    return extracted_data


def RecommendWithReadingPersona(user_reading_personality):

    prompt = f"""Please make 10 book suggestions based on the user's reading personality: {user_reading_personality}
        Explain the each book why you suggested it with 20-30 words. Each book must be on this format: 'title by author: 
        explanation'. Dont add any extra text. just book name, author and explanations about why did you suggest that 
        book."""
        
    reply = make_suggestion(prompt)
        
    extracted_data = extract_books_info(reply)
    print("extracted data:", extracted_data)
    return extracted_data

def RecommendWithParagraph(user_paraghraph):
    logger.info(f"RecommendWithParagraph called: {user_paraghraph}")


    prompt = f"""Please make 10 book suggestions based on the user's book preferences paraghraph: {user_paraghraph}
        Explain the each book why you suggested it with 20-30 words. Each book must be on this format: 'title by author: 
        explanation'. Dont add any extra text. just book name, author and explanations about why did you suggest that 
        book."""
    
    reply = make_suggestion(prompt)
    extracted_data = extract_books_info(reply)
    print("extracted data:", extracted_data)
    return extracted_data
