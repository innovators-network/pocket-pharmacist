// UI helper functions

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
}

function clearChat() {
    const chatContainer = document.getElementById('chatContainer');
    
    // Keep only the welcome message
    while (chatContainer.children.length > 1) {
        chatContainer.removeChild(chatContainer.lastChild);
    }
}