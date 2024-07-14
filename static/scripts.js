document.addEventListener('DOMContentLoaded', function() {
    // Automatically select the default form on page load
    selectForm('form1', 'Form with Questions', 'Use this form to answer specific questions about your reading preferences.');

    // Attach event listener to the form select button to toggle dropdown
    document.getElementById("formSelectBtn").addEventListener('click', toggleDropdown);

    // Attach event listeners to dropdown links
    document.querySelectorAll('.dropdown-content a').forEach(function(link) {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            var formId = link.getAttribute('onclick').match(/selectForm\('([^']+)'\)/)[1];
            var formName = link.textContent;
            var formDescription = link.getAttribute('data-description');
            selectForm(formId, formName, formDescription);
        });

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
    var clickDelay = 30000; // 5 minutes in milliseconds
    var lastClickedTime = parseInt(localStorage.getItem('lastClickedTime')) || 0; // Initialize lastClickedTime
    console.log('Initial lastClickedTime:', lastClickedTime);
    var buttonClicked = false;
    var isAuthenticated = false; // Variable to store authentication status

    function checkAuthentication() {
        return new Promise((resolve, reject) => {
            $.ajax({ 
                headers: { "X-CSRFToken": csrfToken },
                type: 'GET',
                url: '/check_authentication/', // URL for checking authentication status
                dataType: 'json',
                success: function(response) {
                    isAuthenticated = response.is_authenticated;
                    console.log('Authentication status:', isAuthenticated);
                    if (!isAuthenticated) {
                        quickRecommendationButton.prop('disabled', true);
                    }
                    resolve();
                },
                error: function(xhr, status, error) {
                    console.error("Failed to check authentication status", status, error);
                    isAuthenticated = false;
                    quickRecommendationButton.prop('disabled', true);
                    resolve(); // Still resolve to allow flow to continue
                }
            });
        });
    }

    function cooldownActive() {
        var currentTime = new Date().getTime();
        console.log('Current time:', currentTime);
        console.log('Last clicked time:', lastClickedTime);
        var cooldown = lastClickedTime && (currentTime - lastClickedTime < clickDelay);
        console.log('Cooldown active:', cooldown);
        return cooldown;
    }

    function showCooldownMessage(message) {
        var $cooldownMessage = $('#cooldownMessage');
        $cooldownMessage.text(message).show();
        setTimeout(function() {
            $cooldownMessage.hide();
        }, 5000); // Hide after 5 seconds
    }
    $('#recommendationForm').submit(function(event) {
        event.preventDefault();
        console.log('Form submitted:', $(this).attr('id')); // Debugging: Log form submission event
    
        if (cooldownActive()) {
            console.log('Cooldown active, skipping form submission.'); // Debugging: Log cooldown
            showCooldownMessage('Please wait for 5 minutes before requesting again.');
            return;
        }
    
        var form = $(this);
        var action = form.find('input[name="action"]').val(); // Ensure action is correctly set in the form
    
        checkAuthentication().then(() => {
            if (!isAuthenticated && action === 'by_personality') {
                $('#loginWarningModal').modal('show');
                return;
            }
    
            buttonClicked = true;
            console.log('Submitting form:', form.attr('id')); // Debugging: Log form submission
            var currentTime = new Date().getTime();
            localStorage.setItem('lastClickedTime', currentTime.toString());
            console.log('Setting lastClickedTime:', currentTime); // Debugging: Log lastClickedTime setting
            recommendationButton.prop('disabled', true);
            paragraphRecommendationButton.prop('disabled', true);
            quickRecommendationButton.prop('disabled', true);
    
            $('#loadingOverlay').show(); // Show the loading overlay
    
            $.ajax({
                headers: { "X-CSRFToken": csrfToken },
                type: 'POST',
                url: form.attr('action'),
                data: form.serialize(),
                dataType: 'json',
                success: function(response) {
                    if (response.error) {
                        showCooldownMessage(response.error);
                    } else {
                        console.log("Success!", response);
                        displayBooks(response);
                    }
                    buttonClicked = false;
                },
                error: function(xhr, status, error) {
                    console.error("AJAX call failed", status, error);
                    buttonClicked = false;
                },
                complete: function() {
                    $('#loadingOverlay').hide(); // Hide the loading overlay
                    setTimeout(function() {
                        recommendationButton.prop('disabled', false);
                        paragraphRecommendationButton.prop('disabled', false);
                        quickRecommendationButton.prop('disabled', false);
                    }, clickDelay);
                }
            });
        });
    });

        
    $('#paragraphForm, #quickRecommendationForm').submit(function(event) {
        event.preventDefault();
        console.log('Form submitted:', $(this).attr('id')); // Debugging: Log form submission event

        if (cooldownActive()) {
            console.log('Cooldown active, skipping form submission.'); // Debugging: Log cooldown
            showCooldownMessage('Please wait for 5 minutes before requesting again.');
            return;
        }

        var form = $(this);

        checkAuthentication().then(() => {
            if (!isAuthenticated && form.attr('id') === 'quickRecommendationForm') {
                $('#loginWarningModal').modal('show');
                return;
            }

            buttonClicked = true;
            console.log('Submitting form:', form.attr('id')); // Debugging: Log form submission
            var currentTime = new Date().getTime();
            localStorage.setItem('lastClickedTime', currentTime.toString());
            console.log('Setting lastClickedTime:', currentTime); // Debugging: Log lastClickedTime setting
            recommendationButton.prop('disabled', true);
            paragraphRecommendationButton.prop('disabled', true);
            quickRecommendationButton.prop('disabled', true);

            $('#loadingOverlay').show(); // Show the loading overlay

            $.ajax({
                headers: { "X-CSRFToken": csrfToken },
                type: 'POST',
                url: form.attr('action'),
                data: form.serialize(),
                dataType: 'json',
                success: function(response) {
                    if (response.error) {
                        showCooldownMessage(response.error);
                    } else {
                        console.log("Success!", response);
                        displayBooks(response);
                    }
                },
                error: function(xhr, status, error) {
                    console.error("AJAX call failed", status, error);
                },
                complete: function() {
                    buttonClicked = false;
                    $('#loadingOverlay').hide(); // Hide the loading overlay
                    setTimeout(function() {
                        recommendationButton.prop('disabled', false);
                        paragraphRecommendationButton.prop('disabled', false);
                        quickRecommendationButton.prop('disabled', false);
                    }, clickDelay);
                }
            });
        });
    });

    // Initial state based on cooldown
    if (cooldownActive()) {
        recommendationButton.prop('disabled', true);
        paragraphRecommendationButton.prop('disabled', true);
        quickRecommendationButton.prop('disabled', true);
        setTimeout(function() {
            recommendationButton.prop('disabled', false);
            paragraphRecommendationButton.prop('disabled', false);
            quickRecommendationButton.prop('disabled', false);
            $('#cooldownMessage').hide();
        }, clickDelay - (new Date().getTime() - lastClickedTime));
    }

    // Check authentication status initially and fetch cached books
    checkAuthentication().then(() => {
        fetchCachedBooks();
    });

    function fetchCachedBooks() {
        if (!isAuthenticated || buttonClicked) {
            console.log('Skipping fetchCachedBooks:', isAuthenticated, buttonClicked);
            return;
        }

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
            }
        });
    }

    function displayBooks(response) {
        var col1 = $('#column1').empty();
        var col2 = $('#column2').empty();
    
        // Display the header
        $('#aiRecommendationHeader').show();
    
        response.books.forEach(function(book, index) {
            $('#bookColumns').css('display', 'flex');
            var bookDetailLink = $('<a>').attr('href', book.detail_url).text('View Details').addClass('book-detail-link');
            var bookInfoGroup = $('<div class="book-info">')
                .append(
                    $('<h3 class="title">').text(book.name),
                    $('<h3 class="author">').text(book.author),
                    $('<p class="explanation">').text(book.explanation),
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
    
    
    
});



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
                    container.innerHTML = `<p>You need to login to see your read books.</p>`;
                }
            })
            .catch(error => console.error('Error loading the books:', error));
            

        console.log("BOOOKSSS YEAAAH");
        });
        


document.addEventListener('DOMContentLoaded', function() {
    if (!localStorage.getItem('cookieConsent')) {
        document.getElementById('cookie-consent-banner').style.display = 'block';
    }
});

function acceptCookies() {
    localStorage.setItem('cookieConsent', 'true');
    document.getElementById('cookie-consent-banner').style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    console.log("info Document loaded!");
    var infoIcon = document.getElementById('infoIcon');
    var infoSection = document.getElementById('infoSection');

    if (infoIcon) {
        infoIcon.addEventListener('click', function() {
            if (infoSection.style.display === 'none' || infoSection.style.display === '') {
                infoSection.style.display = 'block';
            } else {
                infoSection.style.display = 'none';
            }
        });
    } else {
        console.error("infoIcon not found in the DOM");
    }
});

console.log("Script loaded successfully.");