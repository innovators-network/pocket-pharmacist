let sessionId = null;
let baseUrl = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', function() {
    // Generate a session ID
    sessionId = generateSessionId();
    
    // Set up event listeners
    document.getElementById('sendButton').addEventListener('click', sendMessage);
    document.getElementById('userInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});

function generateSessionId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

async function sendMessage() {
    const inputElement = document.getElementById('userInput');
    const userQuery = inputElement.value.trim();
    
    if (!userQuery) return;
    
    // Add user message to chat
    addMessageToChat(userQuery, 'user');
    
    // Clear input
    inputElement.value = '';
    
    try {
        // Show loading indicator
        const loadingId = addLoadingIndicator();
        
        // Send request to backend
        const response = await fetch(`${baseUrl}/submit_query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: userQuery,
                language: 'auto',  // Always use auto-detection
                session_id: sessionId
            })
        });
        
        // Remove loading indicator
        removeLoadingIndicator(loadingId);
        
        if (!response.ok) {
            throw new Error('Failed to get response');
        }
        
        const data = await response.json();
        
        // Format and display the bot's response
        let botMessage;
        
        if (typeof data.response === 'object') {
            // Handle structured medication information
            botMessage = formatMedicationInfo(data.response);
        } else {
            // Handle simple text response
            botMessage = data.response;
        }
        
        addMessageToChat(botMessage, 'bot');
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('Sorry, I encountered an error. Please try again later.', 'bot');
    }
}

function addMessageToChat(message, sender) {
    const chatContainer = document.getElementById('chatContainer');
    const messageElement = document.createElement('div');
    
    messageElement.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    messageElement.textContent = message;
    
    chatContainer.appendChild(messageElement);
    
    // Scroll to the bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function formatMedicationInfo(info) {
    if (info.response) {
        return info.response;
    }
    
    let formattedText = '';
    
    if (info.brand_name) {
        formattedText += `Medication: ${info.brand_name}\n`;
    }
    
    if (info.generic_name) {
        formattedText += `Generic Name: ${info.generic_name}\n`;
    }
    
    if (info.indications && info.indications[0]) {
        formattedText += `\nUses: ${info.indications[0]}\n`;
    }
    
    if (info.warnings && info.warnings[0]) {
        formattedText += `\nWarnings: ${info.warnings[0]}\n`;
    }
    
    if (info.dosage && info.dosage[0]) {
        formattedText += `\nDosage: ${info.dosage[0]}`;
    }
    
    return formattedText;
}

let loadingCounter = 0;
function addLoadingIndicator() {
    const id = `loading-${loadingCounter++}`;
    const chatContainer = document.getElementById('chatContainer');
    const loadingElement = document.createElement('div');
    
    loadingElement.id = id;
    loadingElement.classList.add('bot-message');
    loadingElement.textContent = 'Thinking...';
    
    chatContainer.appendChild(loadingElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return id;
}

function removeLoadingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}