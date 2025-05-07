document.addEventListener('DOMContentLoaded', () => {
    const messageHistory = document.getElementById('message-history');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    
    // Adam's signature greeting
    setTimeout(() => {
        addMessage('adam', "*kneads clay* Greetings. I am Adam, the first of humankind. Ask me of creation, mercy, or the divine.");
    }, 500);
    
    // Add message to chat (with support for gestures like *kneads clay*)
    function addMessage(sender, text) {
        const message = document.createElement('div');
        message.className = `message ${sender}-message`;
        
        // Format gestures in italics
        const formattedText = text.replace(/\*(.*?)\*/g, '<i>$1</i>');
        message.innerHTML = formattedText;
        
        messageHistory.appendChild(message);
        scrollToBottom();
    }
    
    // Scroll to bottom of chat
    function scrollToBottom() {
        messageHistory.scrollTop = messageHistory.scrollHeight;
    }
    
    // Handle form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        
        if (message) {
            addMessage('user', message);
            userInput.value = '';
            
            // Show Adam's typing indicator (clay-themed)
            const typing = document.createElement('div');
            typing.className = 'message typing-indicator';
            typing.innerHTML = '<i>shapes clay</i> <span>...</span>';
            messageHistory.appendChild(typing);
            scrollToBottom();
            
            // Get Adam's actual response from your Python backend
            try {
                const response = await fetchAdamResponse(message);
                messageHistory.removeChild(typing);
                addMessage('adam', response);
            } catch (error) {
                messageHistory.removeChild(typing);
                addMessage('adam', getFallbackResponse(message));
                console.error("API error:", error);
            }
        }
    });
    
    // Fetch response from your Python backend
    async function askAdam(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: getUserId(),
                message: message
            })
        });
        return await response.json();
    }
    
    // Fallback responses if API fails (in Adam's style)
    function getFallbackResponse(query) {
        const lowerQuery = query.toLowerCase();
        const fallbacks = {
            'creation': "*crumbles clay* I recall... humans were shaped from clay by the Hand Divine.",
            'mercy': "*touches chest* The Lord's mercy is vaster than the heavens.",
            'eve': "*shapes two figures* She was made from my rib, my companion in Eden.",
            'default': "*kneads clay* My connection to sacred knowledge falters. Ask again."
        };
        
        if (lowerQuery.includes('create') || lowerQuery.includes('made')) {
            return fallbacks.creation;
        } else if (lowerQuery.includes('mercy') || lowerQuery.includes('forgive')) {
            return fallbacks.mercy;
        } else if (lowerQuery.includes('eve') || lowerQuery.includes('wife')) {
            return fallbacks.eve;
        } else {
            return fallbacks.default;
        }
    }
    
    // Allow Shift+Enter for new lines, Enter to send
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
        // When ADAM sends a response:
    const responseData = {
        query: userQuestion,
        response: aiResponse,
        responseId: 'res-' + Date.now(),
        timestamp: new Date().toISOString()
    };
    localStorage.setItem('adam-interaction', JSON.stringify(responseData));
    localStorage.removeItem('adam-interaction'); // Trigger event
});