/**
 * VULNERABLE: Reflected XSS.
 * This script takes input from the URL and injects it directly into the DOM
 * without any sanitization.
 */

function displayFeedback() {
    // Get the feedback message from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const feedbackMsg = urlParams.get('msg');
    
    if (feedbackMsg) {
        const feedbackContainer = document.getElementById('feedback-container');
        
        // CRITICAL: Directly setting innerHTML with user-controlled input
        feedbackContainer.innerHTML = "<h4>Your Feedback:</h4><p>" + feedbackMsg + "</p>";
    }
}

function updateUsernameDisplay() {
    const username = localStorage.getItem('current_user');
    
    if (username) {
        // VULNERABLE: Another XSS point
        document.getElementById('user-welcome').innerHTML = "Welcome back, <b>" + username + "</b>!";
    }
}

// Initialize
window.onload = function() {
    displayFeedback();
    updateUsernameDisplay();
};
