import openai
import json
from aifolder.extract_book_data import extract_book_and_author as ed
from projects.management.commands import addbooks 



functions = [
{
        "type": "function",
        "function": {
            "name": "by_users_description",
            "description": "Make book suggestions for the user based on user's description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "Users Description": {
                        "type": "string",
                        "description": "User's description about how books they like , e.g. I "
                                       "prefer books that focus on human relationships, historical events, "
                                       "and emotional depth. Additionally, they value stories enriched with historical "
                                       "details and character development. Like Martin Eden and Jack London's other books."
                    },
                },
                "required": ["users_description"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "by_book_titles",
            "description": "Make book suggestions for the user based on book title or titles",
            "parameters": {
                "type": "object",
                "properties": {
                    "Book title or titles": {
                        "type": "string",
                        "description": "A book's title , e.g. Martin Eden, Harry Potter",
                    },
                },
                "required": ["Book title or titles"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "by_book_authors",
            "description": "Make book suggestions for the user based on book author or authors",
            "parameters": {
                "type": "object",
                "properties": {
                    "book author or authors": {
                        "type": "string",
                        "description": "A book's author, e.g. Jack London, J.K. Rowling",
                    },
                },
                "required": ["book author or authors"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "by_book_authors_and_titles",
            "description": "Make book suggestions for the user based on book authors and book titles",
            "parameters": {
                "type": "object",
                "properties": {
                    "book author or authors": {
                        "type": "string",
                        "description": "A book's author, e.g. Jack London, J.K. Rowling",
                    },
                    "Book title or titles": {
                        "type": "string",
                        "description": "A book's title , e.g. Martin Eden, Harry Potter",
                    },
                },
                "required": ["book author or authors", "Book title or titles"]
            },
        }
    },
]

with open('C:/project_bookai/aifolder/openaikey.txt', 'r') as file:
    # Read the entire content of the file
    content = file.read()
    

openai.api_key = content


output_example = """Based on your interest in Martin Eden by Jack London, I would suggest exploring these titles:\n
1. Sister Carrie by Theodore Dreiser.
2. The Red Badge of Courage by Stephen Crane.
3. The Jungle by Upton Sinclair.
4. The Call of the Wild by Jack London.
5. McTeague by Frank Norris.\n
All of these authors share Jack London's knack for raw, naturalistic storytelling that dives deep into the human spirit. Just as Martin Eden, these books will transport you back in time, while tackling profound themes. I hope you enjoy them."""


messages = [
    {
        "role": "assistant",
        "content": "Don't make assumptions about what values to plug into functions. Run the suitable function."
    },
    {
        "role": "system",
        f"content": f"You are an intelligent book suggester AI and you know about books. Your task is to suggest books "
                   "for the users based on their input. After providing book suggestions, craft a friendly and "
                   "informative response to the user, incorporating these suggestions. Your book recommendations "
                   "should be in the format: 'title by author'. Avoid suggesting the same author's books repeatedly. "
                   "Do not use quotation marks around book names, and do not use 'and' between book names. Each book "
                   "name should be followed by a period. Example output must be like this: " + output_example
    }
]

def by_book_titles(book_names, upvote_books):
    return make_suggestion(book_names, upvote_books)
def by_book_authors(authors, upvote_books):
    return make_suggestion(authors, upvote_books)
def by_book_titles_and_authors(summed_data, upvote_books):
    return make_suggestion(summed_data, upvote_books)

def by_users_description(desc, upvote_books):
    return make_suggestion(desc, upvote_books)


def make_suggestion(data, upvote_books):
    while True:
        one_message = f"Make 5 book suggestions based on the parameters of the user: {data} First, suggest 5 book Then, provide a friendly and engaging response to the user as if you are a knowledgeable book assistant."

        if one_message:
            messages.append(
                {"role": "user", "content": one_message},
            )

            chat = openai.chat.completions.create( #type: ignore
                model="gpt-4", messages=messages #type: ignore
            )
        print(chat)#type: ignore
        reply = chat.choices[0].message.content#type: ignore

        recommended_books = ed(reply)

        print(reply)
        return recommended_books
def gpt_main(user_query, upvote_books):

    while True:
        message = user_query

        if message:
            messages.append(
                {"role": "user", "content": message},
            )
            chat = openai.chat.completions.create(#type: ignore
                model="gpt-4", messages=messages, tools=functions, #type: ignore
            )
        recommended_books = []
        tool_calls = chat.choices[0].message.tool_calls#type: ignore
        for tool_call in tool_calls: #type: ignore
            function_name = tool_call.function.name
            arguments_data = tool_call.function.arguments
            arguments = json.loads(arguments_data)

            if function_name == "by_book_titles":
                book_names = arguments["Book title or titles"]
                recommended_books=by_book_titles(book_names, upvote_books)
                print(recommended_books)
                addbooks.add_books(recommended_books[0])
                return recommended_books
            elif function_name == "by_book_authors":
                authors = arguments["book author or authors"]
                recommended_books= by_book_authors(authors, upvote_books)
                addbooks.add_books(recommended_books[0])
                return recommended_books
            elif function_name == "by_book_authors_and_titles":
                book_names = arguments["Book title or titles"]
                authors = arguments["book author or authors"]
                summed_data = f"The book i like: {book_names}. The author i like: {authors}"
                recommended_books=by_book_titles_and_authors(summed_data, upvote_books)
                addbooks.add_books(recommended_books[0])
                return recommended_books
            elif function_name == "by_users_description":
                description = arguments["Users Description"]
                recommended_books=by_users_description(description, upvote_books)
                addbooks.add_books( recommended_books[0])
                return recommended_books
        reply = chat.choices[0].message.content # type: ignore
        print(chat)#type: ignore
        messages.append({"role": "assistant", "content": reply}) #type: ignore

        return recommended_books
