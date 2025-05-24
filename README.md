# BookHalter

BookHalter is my first project, created while learning Django and web development during my first year at university. It’s not well-structured, the design is terrible, and it's far from being maintenance-friendly. But it holds a special place in my heart.

This is the first project where I spent three days straight solving just one bug. It’s also the first time I experienced the joy of building something from scratch.

BookHalter is a Django-based web application that helps users discover their next read through AI-powered recommendations. It fetches book information from Google Books and presents it in a friendly and simple user interface.



## 🚀 Features

- Book recommendations using OpenAI APIs
- Fetches book information from the Google Books API
- Detailed book pages with voting, commenting, and buy links
- Responsive and user-friendly web interface
- Basic rate-limiting protection
- Static file handling with WhiteNoise

## 🛠️ Technologies Used

- Python 3.x
- Django 5.0
- OpenAI integration
- Django AllAuth for authentication
- Beautiful Soup 4 for web scraping
- Pillow for image processing
- And more (see requirements.txt for full list)

## 📋 Prerequisites

- Python 3.x
- Virtual environment (recommended)
- Git

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Ernosto0/BookHalter.git
   cd BookHalter
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000`

## 🔐 Environment Variables

Create a `.env` file in the root directory and add the following variables:
```
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 📁 Project Structure

- `bookhalter/` - Main Django project configuration
- `users/` - User management app
- `projects/` - Project-specific functionality
- `templates/` - HTML templates
- `static/` - Static files (CSS, JavaScript, images)
- `staticfiles/` - Collected static files for production
- `aifolder/` - AI-related functionality

## 🤝 Contributing

I don't recommend it

