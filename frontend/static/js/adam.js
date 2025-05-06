document.addEventListener('DOMContentLoaded', () => {
    const messageHistory = document.getElementById('message-history');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    
    // Initial greeting
    setTimeout(() => {
        addMessage('adam', "Hello. I'm ADAM, an AI designed to help with thoughtful consideration. How can I assist you today?");
    }, 500);
    
    // Add message to chat
    function addMessage(sender, text) {
        const message = document.createElement('div');
        message.className = `message ${sender}-message`;
        message.textContent = text;
        messageHistory.appendChild(message);
        scrollToBottom();
    }
    
    // Scroll to bottom of chat
    function scrollToBottom() {
        messageHistory.scrollTop = messageHistory.scrollHeight;
    }
    
    // Handle form submission
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        
        if (message) {
            addMessage('user', message);
            userInput.value = '';
            
            // Show typing indicator
            const typing = document.createElement('div');
            typing.className = 'message typing-indicator';
            typing.innerHTML = '<span></span><span></span><span></span>';
            messageHistory.appendChild(typing);
            scrollToBottom();
            
            // Simulate response after delay
            setTimeout(() => {
                messageHistory.removeChild(typing);
                getAIResponse(message);
            }, 1500);
        }
    });
    
    // Get AI response (simulated)
    function getAIResponse(query) {
        // In a real implementation, this would call your backend API
        const responses = [
            "I've considered your question carefully. Here's what I can share...",
            "That's an interesting perspective. From my analysis...",
            "After reviewing available information, I'd suggest...",
            "Let me think about that. My understanding is...",
            "I appreciate your question. The key points are..."
        ];
        
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        addMessage('adam', randomResponse);
    }
    
    // Allow Shift+Enter for new lines, Enter to send
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
});