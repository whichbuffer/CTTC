$(document).ready(function() {
    const currentTheme = localStorage.getItem('theme');
    
    if (currentTheme) {
        document.body.dataset.theme = currentTheme;
    }

    // Your original code for the form submit
    $('#threatForm').on('submit', function() {
        $('#submitButton').prop('disabled', true);
        $('#loadingSpinner').show();
    });

    // Event listener for theme change (make sure #themeToggle exists in your HTML!)
    $("#themeToggle").on('click', function() {
        let currentTheme = document.body.dataset.theme;

        // Toggle the theme
        if (currentTheme === "dark") {
            document.body.dataset.theme = "light";
            localStorage.setItem('theme', 'light');
        } else {
            document.body.dataset.theme = "dark";
            localStorage.setItem('theme', 'dark');
        }
    });
});
