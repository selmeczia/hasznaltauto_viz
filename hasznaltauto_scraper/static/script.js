document.addEventListener('DOMContentLoaded', function () {
    var myForm = document.getElementById('linkForm');
    var submitBtn = document.getElementById('submitBtn');
    var loadingSpinner = document.getElementById('loadingSpinner');

    myForm.addEventListener('submit', function (event) {
        // Prevent the form from submitting normally
        event.preventDefault();

        // Get the input value
        const linkInput = document.getElementById('input_link');
        const linkValue = linkInput.value;

        const allowedDomain = 'hasznaltauto.hu';
        const correctLink = 'hasznaltauto.hu/talalatilista/'

        var modalText = document.getElementById('textModal');

        if (linkValue.includes(correctLink)) {
            // Link is correct

            // Show the overlay (fade the screen)
            var overlay = document.getElementById('overlay');
            overlay.style.display = 'flex';
    
            // Show the spinner and disable the submit button during form submission
            loadingSpinner.style.display = 'flex';
            submitBtn.disabled = true;
    
            // Submit form
            myForm.submit()

          } else if (linkValue.includes(allowedDomain)) {
            // Link is not a search result

            $('#errorModal').modal('show');
            modalText.textContent = "A megadott link nem egy keresési eredmény linkje!"
            
        } else {
            // Link is not from allowed domain
            
            $('#errorModal').modal('show');
            modalText.textContent = "A megadott link nem megfelelő!"

          }

    });
});
