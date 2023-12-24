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

openai.api_key = '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'

messages = [
    {
        "role": "system",
        "content": "Don't make assumptions about what values to plug into functions. Dont chat with user. Just run "
                   "the suitable function."
    },
    {
        "role": "system",
        "content": f"You are an intelligent book suggester Ai and you know about books. Your task is suggesting books "
                   f"for the users. You are not going to chat with users. Don't add any extra text. Your task is to "
                   f"recommend books based on the user's input.Your responses should be in this format: "
                   f"{'title by author'} (without 'f' symbols). If the user's message is: 'Make suggestions based on "
                   f"my parameters,' do that: Make book suggestions based on the parameters of the user data ("
                   f"This user data could be book names or author names are both. You need to make best book "
                   f"suggestions for people that like these book and authors. Dont suggest same author's books "
                   f"constantly.).Dont say 'and' between two books. ADD"
                   f"a '.' after book name. Dont add quotation mark between book name."
    }
]


def by_book_titles(book_names):
    return make_suggestion(book_names)
def by_book_authors(authors):
    return make_suggestion(authors)
def by_book_titles_and_authors(summed_data):
    return make_suggestion(summed_data)

def by_users_description(desc):
    return make_suggestion(desc)


def make_suggestion(data):
    while True:
        one_message = f"Make 5 book suggestions based on the parameters of the user: {data}"

        if one_message:
            messages.append(
                {"role": "user", "content": one_message},
            )
            chat = openai.chat.completions.create( #type: ignore
                model="gpt-4", messages=messages #type: ignore
            )
        print(chat)#type: ignore
        reply = chat.choices[0].message.content#type: ignore

        recomended_books = ed(reply)

        print(reply)
        return recomended_books
def gpt_main(user_query):

    while True:
        message = user_query

        if message:
            messages.append(
                {"role": "user", "content": message},
            )
            chat = openai.chat.completions.create(#type: ignore
                model="gpt-4", messages=messages, tools=functions, #type: ignore
            )
        recomennded_books = []
        tool_calls = chat.choices[0].message.tool_calls#type: ignore
        for tool_call in tool_calls: #type: ignore
            function_name = tool_call.function.name
            arguments_data = tool_call.function.arguments
            arguments = json.loads(arguments_data)

            if function_name == "by_book_titles":
                book_names = arguments["Book title or titles"]
                recomennded_books=by_book_titles(book_names)
                print(recomennded_books)
                addbooks.add_books( recomennded_books)
                return recomennded_books
            elif function_name == "by_book_authors":
                authors = arguments["book author or authors"]
                recomennded_books= by_book_authors(authors)
                addbooks.add_books( recomennded_books)
                return recomennded_books
            elif function_name == "by_book_authors_and_titles":
                book_names = arguments["Book title or titles"]
                authors = arguments["book author or authors"]
                summed_data = f"The book i like: {book_names}. The author i like: {authors}"
                recomennded_books=by_book_titles_and_authors(summed_data)
                addbooks.add_books( recomennded_books)
                return recomennded_books
            elif function_name == "by_users_description":
                description = arguments["Users Description"]
                recomennded_books=by_users_description(description)
                addbooks.add_books( recomennded_books)
                return recomennded_books
        reply = chat.choices[0].message.content # type: ignore
        print(chat)#type: ignore
        messages.append({"role": "assistant", "content": reply}) #type: ignore

        return recomennded_books
