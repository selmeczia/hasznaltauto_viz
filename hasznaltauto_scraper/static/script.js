window.addEventListener("pageshow", function(event) {
    var overlay = document.getElementById('overlay');
    var submitBtn = document.getElementById('submitBtn');
    var loadingSpinner = document.getElementById('loadingSpinner');

    if (overlay) {
        overlay.style.display = 'none';
        loadingSpinner.style.display = 'none';
        submitBtn.disabled = false;
    }
});

document.addEventListener('DOMContentLoaded', function () {
    var myForm = document.getElementById('linkForm');
    var submitBtn = document.getElementById('submitBtn');
    var loadingSpinner = document.getElementById('loadingSpinner');

    myForm.addEventListener('submit', function (event) {
        // Prevent the form from submitting normally
        event.preventDefault();

        // Show the overlay (fade the screen)
        var overlay = document.getElementById('overlay');
        overlay.style.display = 'flex';

        // Show the spinner and disable the submit button during form submission
        loadingSpinner.style.display = 'flex';
        submitBtn.disabled = true;

        // Submit form
        myForm.submit()
    });
});
