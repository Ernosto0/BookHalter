
import openai
import sqlite3
from aifolder import aimessage as aim
from aifolder import extract_book_data as ed
from projects.management.commands import addbooks
def gpt_main(request):
    recomended_books = []
    openai.api_key = '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'
    while True:
        message = f"Make 5 book suggestions based on the parameters of the user: {aim.userdata}"

        if message:
            aim.aqmessages.append(
                {"role": "user", "content": message},
            )
            chat = openai.chat.completions.create(
                model="gpt-4", messages= aim.aqmessages # type: ignore
   
            )
        reply = chat.choices[0].message.content # type: ignore
        print(reply)
        recomended_books = ed.ex(reply)
        aim.aqmessages.append({"role": "assistant", "content": reply}) # type: ignore
        print(request)
        print(recomended_books)
        addbooks.add_books(recomended_books)  
        
        return recomended_books

        
