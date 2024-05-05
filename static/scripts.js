$(document).ready(function() {
    $('#recommendationForm').submit(function(event) {
        event.preventDefault();
        var actionUrl = $(this).data('url');  // Fetch the URL from data attribute

        $.ajax({
            headers: { "X-CSRFToken": $('meta[name="csrf-token"]').attr('content') }, // Assuming you have <meta name="csrf-token" content="{{ csrf_token }}">
            type: 'POST',
            url: actionUrl,  // Use the fetched URL here
            data: $(this).serialize(),
            dataType: 'json',
            success: function(response) {
                var col1 = $('#column1').empty();
                var col2 = $('#column2').empty();
                response.books.forEach(function(book, index) {
                    var bookDetailLink = $('<a>').attr('href', book.detail_url).text('View Details').addClass('book-detail-link');
                    var bookElement = $('<div class="book">').append(
                        $('<h3 class="title">').text(book.name),
                        book.cover_image_url ? $('<img>').attr('src', book.cover_image_url) : '',
                        $('<p>').text('Author: ' + book.author),
                        $('<p>').text(book.explanation),
                        bookDetailLink
                    );
                    if (index % 2 === 0) { col1.append(bookElement); }
                    else { col2.append(bookElement); }
                });
            },
            error: function(xhr, status, error) {
                console.error("AJAX call failed", status, error);
            }
        });
    });
});


document.addEventListener('DOMContentLoaded', function() {
    var fetchUrl = document.body.getAttribute('data-get-read-books-url');
    fetch(fetchUrl)
    .then(response => response.json())
    .then(data => {
        let books = data.read_books;
        let container = document.getElementById('readBooksList');
        container.innerHTML = ''; // Clear existing entries
        if (books.length) {
            books.forEach(book => {
                // Entire book entry is now clickable
                let bookDiv = `<a href="${book.url}" style="text-decoration: none; color: inherit;">
                                <div class="read-book">
                                    <h4>${book.name}</h4>
                                    <p>${book.author}</p>
                                </div>
                            </a>`;
                container.innerHTML += bookDiv;
            });
        } else {
            container.innerHTML = '<p>You haven\'t marked any books as read yet.</p>';
        }
    })
    .catch(error => console.error('Error loading the books:', error));
});

// login modal script
// Get the modal
var modal = document.getElementById('loginModal');

// Get the button that opens the modal
var loginBtn = document.getElementById('loginBtn');

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal
loginBtn.onclick = function() {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Get the modal
var registerModal = document.getElementById('registerModal');

// Get the button that opens the modal
var registerBtn = document.getElementById('registerBtn');  // Ensure this button is added somewhere on your page

// Get the <span> element that closes the modal
var spanRegister = document.getElementsByClassName("close-register")[0];

// When the user clicks on the button, open the modal
registerBtn.onclick = function() {
    registerModal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
spanRegister.onclick = function() {
    registerModal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == registerModal) {
        registerModal.style.display = "none";
    }
}


// Loader
$(document).ready(function() {
    var csrfToken = $('body').data('csrf-token');
    var actionUrl = $('body').data('url');

    $('#recommendationForm').submit(function(event) {
        event.preventDefault();
        $('#loading').show(); // Show the loader

        $.ajax({
            headers: { "X-CSRFToken": csrfToken },
            type: 'POST',
            url: actionUrl,
            data: $(this).serialize(),
            dataType: 'json',
            success: function(response) {
                // Process response
                console.log("Success!");
            },
            error: function(xhr, status, error) {
                console.error("AJAX call failed", status, error);
            },
            complete: function() {
                $('#loading').hide(); // Hide the loader
                console.log("Loader hidden.");
            }
        });
    });
});



console.log("Script loaded successfully.");