document.addEventListener('DOMContentLoaded', function() {
    // Automatically select the default form on page load
    selectForm('form1', 'Form with Questions', 'Use this form to answer specific questions about your reading preferences.');
});

function selectForm(formId, formName, formDescription) {
    // Update the button text to show the selected form name
    document.getElementById("formSelectBtn").textContent = formName;
    // Update the description above the dropdown
    document.getElementById("formDescription").textContent = formDescription;
    // Show the selected form
    showForm(formId);
}

function showForm(formId) {
    var forms = document.getElementsByClassName('form-container');
    for (var i = 0; i < forms.length; i++) {
        forms[i].style.display = 'none'; // Hide all forms
    }
    document.getElementById(formId).style.display = 'block'; // Show selected form
    // Ensure the dropdown menu is closed after selection
    closeDropdown();
}

function toggleDropdown() {
    document.getElementById("formDropdown").classList.toggle("show");
}

function closeDropdown() {
    var dropdowns = document.getElementsByClassName("dropdown-content");
    for (var i = 0; i < dropdowns.length; i++) {
        dropdowns[i].classList.remove('show');
    }
}

// Handle clicks outside the dropdown to close it
window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
        closeDropdown();
    }
}

// Show description on hover
document.querySelectorAll('.dropdown-content a').forEach(function(link) {
    link.addEventListener('mouseover', function() {
        var description = link.getAttribute('data-description');
        document.getElementById('formDescription').textContent = description;
    });
    link.addEventListener('mouseout', function() {
        // Reset to the selected form's description
        var selectedForm = document.getElementById("formSelectBtn").textContent;
        if (selectedForm === "Form with Questions") {
            document.getElementById('formDescription').textContent = "Use this form to answer specific questions about your reading preferences.";
        } else if (selectedForm === "Form with Paragraph") {
            document.getElementById('formDescription').textContent = "Use this form to describe your reading preferences in a paragraph.";
        } else {
            document.getElementById('formDescription').textContent = 'Select a form to see more details.';
        }
    });
});





$(document).ready(function() {
    console.log("Document ready!");
    var csrfToken = $('meta[name="csrf-token"]').attr('content');
    var recommendationButton = $('#recBtn');
    var paragraphRecommendationButton = $('#paraBtn');
    var quickRecommendationButton = $('#quickRecBtn');
    var clickDelay = 300000; // 5 minutes in milliseconds
    var lastClickedTime = parseInt(localStorage.getItem('lastClickedTime'));
    var buttonClicked = false;
    var isAuthenticated = false; // Variable to store authentication status

    // Function to check authentication status
    function checkAuthentication(callback) {
        $.ajax({
            headers: { "X-CSRFToken": csrfToken },
            type: 'GET',
            url: '/check_authentication/', // URL for checking authentication status
            dataType: 'json',
            success: function(response) {
                isAuthenticated = response.is_authenticated;
                if (!isAuthenticated) {
                    quickRecommendationButton.prop('disabled', true);
                }
                if (callback) callback();
            },
            error: function(xhr, status, error) {
                console.error("Failed to check authentication status", status, error);
                isAuthenticated = false;
                quickRecommendationButton.prop('disabled', true);
                if (callback) callback();
            }
        });
    }

    function cooldownActive() {
        var currentTime = new Date().getTime();
        return lastClickedTime && (currentTime - lastClickedTime < clickDelay);
    }

    function fetchCachedBooks() {
        checkAuthentication(function() {
            if (!isAuthenticated) {
                // Do not fetch cached books if the user is not authenticated
                return;
            }
            if (!buttonClicked) { // Only fetch cached books if the button is not clicked
                $.ajax({
                    headers: { "X-CSRFToken": csrfToken },
                    type: 'GET',
                    url: '/get_cached_books/', // URL for fetching cached books
                    dataType: 'json',
                    success: function(response) {
                        displayBooks(response);
                    },
                    error: function(xhr, status, error) {
                        console.error("AJAX call failed", status, error);
                        console.error("Error details:", xhr.responseText);
                    }
                });
            }
        });
    }

    if (cooldownActive()) {
        recommendationButton.prop('disabled', true);
        paragraphRecommendationButton.prop('disabled', true);
        quickRecommendationButton.prop('disabled', true);
        setTimeout(function() {
            recommendationButton.prop('disabled', false);
            paragraphRecommendationButton.prop('disabled', false);
            quickRecommendationButton.prop('disabled', false);
            alert('You can now request recommendations again.');
        }, clickDelay - (new Date().getTime() - lastClickedTime));
    }

    $('#formSelectBtn').click(function() {
        toggleDropdown();
    });

    $('#recommendationForm, #paragraphForm, #quickRecommendationForm').submit(function(event) {
        event.preventDefault();

        if (cooldownActive()) {
            alert('Please wait for 5 minutes before requesting again!');
            return;
        }

        var form = $(this);

        checkAuthentication(function() {
            // Check if user is authenticated
            if (!isAuthenticated && form.attr('id') === 'quickRecommendationForm') {
                $('#loginWarningModal').modal('show');
                return;
            }

            buttonClicked = true;
            console.log('Submitting form:', form.attr('id')); // Debugging: Log form submission
            var currentTime = new Date().getTime();
            localStorage.setItem('lastClickedTime', currentTime.toString());
            recommendationButton.prop('disabled', true);
            paragraphRecommendationButton.prop('disabled', true);
            quickRecommendationButton.prop('disabled', true);

            $('#loading').show();

            $.ajax({
                headers: { "X-CSRFToken": csrfToken },
                type: 'POST',
                url: form.attr('action'),
                data: form.serialize(),
                dataType: 'json',
                success: function(response) {
                    console.log("Success!", response);
                    displayBooks(response);
                    buttonClicked = false;
                },
                error: function(xhr, status, error) {
                    console.error("AJAX call failed", status, error);
                    console.error("Error details:", xhr.responseText);
                    buttonClicked = false;
                },
                complete: function() {
                    $('#loading').hide();
                    setTimeout(function() {
                        recommendationButton.prop('disabled', false);
                        paragraphRecommendationButton.prop('disabled', false);
                        quickRecommendationButton.prop('disabled', false);
                    }, clickDelay);
                }
            });
        });
    });

    checkAuthentication(fetchCachedBooks); // Check authentication status and fetch cached books on page load
});

function displayBooks(response) {
    $('#bookColumns').css('display', 'flex');
    var col1 = $('#column1').empty();
    var col2 = $('#column2').empty();
    response.books.forEach(function(book, index) {
        var bookDetailLink = $('<a>').attr('href', book.detail_url).text('View Details').addClass('book-detail-link');
        var bookInfoGroup = $('<div class="book-info">')
            .append(
                $('<h3 class="title">').text(book.name),
                $('<h3 class="author">').text(book.author),
                $('<h3 class="explanation">').text(book.explanation),
                bookDetailLink
            );
        var bookElement = $('<div class="book">').append(
            book.cover_image_url ? $('<img class="img">').attr('src', book.cover_image_url) : '',
            bookInfoGroup
        );
        if (index % 2 === 0) {
            col1.append(bookElement);
        } else {
            col2.append(bookElement);
        }
    });
}








        document.addEventListener('DOMContentLoaded', function() {
            console.log("DOM loaded!");
            var fetchUrl = document.body.getAttribute('data-get-read-books-url');
            fetch(fetchUrl)
            .then(response => response.json())
            .then(data => {
                console.log('API Response:', data); // Log the entire response for debugging
        
                let container = document.getElementById('readBooksList');
                container.innerHTML = ''; // Clear existing entries
        
                if (data.authenticated) {
                    if (data.read_books && data.read_books.length) {
                        data.read_books.forEach(book => {
                            // Entire book entry is now clickable
                            let bookDiv = document.createElement('a');
                            bookDiv.href = book.url;
                            bookDiv.style.textDecoration = 'none';
                            bookDiv.style.color = 'inherit';
        
                            let bookContent = `
                                <div class="read-book">
                                    <h4>${book.name}</h4>
                                    <p>${book.author}</p>
                                </div>`;
                            
                            bookDiv.innerHTML = bookContent;
                            container.appendChild(bookDiv);
                        });
                    } else {
                        container.innerHTML = '<p>You haven\'t marked any books as read yet.</p>';
                    }
                } else {
                    container.innerHTML = `<p>${data.error || 'You need to login to see read books.'}</p>`;
                }
            })
            .catch(error => console.error('Error loading the books:', error));
            

        console.log("BOOOKSSS YEAAAH");
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

document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent the default form submission
    var form = event.target;
    var formData = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        var errorDiv = document.getElementById('login-error');
        var messageDiv = document.getElementById('login-message');
        if (data.success) {
            errorDiv.textContent = '';  // Clear any previous errors
            messageDiv.textContent = 'Login successful!';
            setTimeout(() => {
                window.location.reload();  // Optionally reload the page after a short delay
            }, 2000);  // Adjust delay as needed
        } else {
            messageDiv.textContent = '';  // Clear any previous success messages
            errorDiv.textContent = data.error;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});


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


// Register form submission
document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent the default form submission
    var form = event.target;
    var formData = new FormData(form);

    // Convert FormData to URLSearchParams
    var urlParams = new URLSearchParams();
    formData.forEach((value, key) => {
        urlParams.append(key, value);
    });

    console.log("Submitting form with data:", urlParams.toString());  // Log form data for debugging

    fetch(form.action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',  // Ensure X-Requested-With header is set
            'Content-Type': 'application/x-www-form-urlencoded'  // Ensure content type is correct
        },
        body: urlParams.toString()  // Send data as URL-encoded string
    })
    .then(response => {
        console.log("Response status:", response.status);  // Log response status
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        var errorDiv = document.getElementById('register-error');
        var successDiv = document.getElementById('register-success');
        if (data.success) {
            errorDiv.textContent = '';  // Clear any previous errors
            successDiv.textContent = 'Registration successful!';
            setTimeout(() => {
                document.getElementById('registerModal').style.display = 'none';
                successDiv.textContent = '';  // Clear success message after closing modal
            }, 2000);  // Adjust delay as needed
        } else {
            console.error("Form errors:", data.error);  // Log form errors
            successDiv.textContent = '';  // Clear any previous success messages
            errorDiv.innerHTML = '';  // Clear previous error messages
            // Check if data.error is a string and handle it
            if (typeof data.error === 'string') {
                var p = document.createElement('p');
                p.textContent = data.error;
                errorDiv.appendChild(p);
            } else {
                // Iterate through errors and display them
                for (let field in data.error) {
                    if (data.error.hasOwnProperty(field)) {
                        data.error[field].forEach(error => {
                            var p = document.createElement('p');
                            p.textContent = `${field}: ${error}`;
                            errorDiv.appendChild(p);
                        });
                    }
                }
            }
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);  // Log fetch errors
        var errorDiv = document.getElementById('register-error');
        errorDiv.textContent = 'An unexpected error occurred. Please try again later.';
    });
});

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    var registerModal = document.getElementById('registerModal');
    if (event.target == registerModal) {
        registerModal.style.display = "none";
    }
}





// Loader
// $(document).ready(function() {
//     var csrfToken = $('body').data('csrf-token');
//     var actionUrl = $('body').data('url');

//     $('#recommendationForm').submit(function(event) {
//         event.preventDefault();
//         $('#loading').show(); // Show the loader

//         $.ajax({
//             headers: { "X-CSRFToken": csrfToken },
//             type: 'POST',
//             url: actionUrl,
//             data: $(this).serialize(),
//             dataType: 'json',
//             success: function(response) {
//                 try {
//                     var jsonData = JSON.parse(response);
//                     console.log("Success!", jsonData);
//                 } catch (e) {
//                     console.error("Failed to parse JSON:", response);
//                 }
//             },
//             error: function(xhr, status, error) {
//                 console.error("AJAX call failed", status, error);
//             },
//             complete: function() {
//                 $('#loading').hide(); // Hide the loader
//                 console.log("Loader hidden.");
//             }
//         });
//     });
// });


// Logout script
document.getElementById('logoutButton').addEventListener('click', function() {
    // Directly use the CSRF token provided by Django
    const csrfToken = '{{ csrf_token }}';
    console.log("CSRF Token:", csrfToken);  // Log the CSRF token for debugging

    // Define the URL directly
    const logoutUrl = '{% url "logout" %}';

    // Perform the fetch request
    fetch(logoutUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded'  // Ensure content type is correct
        },
        body: ''  // Empty body for POST request
    }).then(response => {
        console.log("Response Status:", response.status);  // Log response status for debugging
        var logoutMessageDiv = document.getElementById('logout-message');
        if (response.ok) {
            logoutMessageDiv.textContent = 'You have been logged out successfully.';
            setTimeout(() => {
                location.reload();  // Optionally reload the page after a short delay
            }, 2000);  // Adjust delay as needed
        } else {
            return response.text().then(text => { throw new Error(text) });  // Capture detailed error message
        }
    }).catch(error => {
        console.error('Error:', error);  // Log detailed error to console
        var logoutMessageDiv = document.getElementById('logout-message');
        // logoutMessageDiv.textContent = 'Logout failed: ' + error.message;  // Display detailed error message
        logoutMessageDiv.style.color = 'red';  // Change color to red for errors
    });
});


console.log("Script loaded successfully.");