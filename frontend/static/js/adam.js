document.addEventListener('DOMContentLoaded', () => {
    const messageHistory = document.getElementById('message-history');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    
    // Adam's signature greeting
    setTimeout(() => {
        addMessage('adam', "*kneads clay* Greetings. I am Adam, the first of humankind. Ask me of creation, mercy, or the divine.");
    }, 500);
    
    function addMessage(sender, text) {
        const message = document.createElement('div');
        message.className = `message ${sender}-message`;
        const formattedText = text.replace(/\*(.*?)\*/g, '<i>$1</i>');
        message.innerHTML = formattedText;
        messageHistory.appendChild(message);
        scrollToBottom();
    }
    
    function scrollToBottom() {
        messageHistory.scrollTop = messageHistory.scrollHeight;
    }
    
    async function fetchAdamResponse(message) {
    try {
        console.log('[Frontend] Sending message:', message);
        
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                user_id: getUserId(),
                message: message
            })
        });

        console.log('[Frontend] Received response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('[Frontend] Full response data:', data);
        
        if (data.status !== 'success') {
            throw new Error(data.response || 'Unknown error from server');
        }

        return data.response;
    } catch (error) {
        console.error('[Frontend] Error in fetchAdamResponse:', error);
        throw error;
    }
}

    // Update your chat form event listener
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
    
        if (!message) return;

        addMessage('user', message);
        userInput.value = '';
    
        // Show typing indicator
        const typing = addTypingIndicator();
    
        try {
            const response = await fetchAdamResponse(message);
            messageHistory.removeChild(typing);
        
            // Ensure we have a response to display
            if (response) {
                addMessage('adam', response);
            } else {
                addMessage('adam', getFallbackResponse(message));
            }
        
        } catch (error) {
            console.error('[Frontend] Chat error:', error);
            messageHistory.removeChild(typing);
            addMessage('adam', getFallbackResponse(message));
        }
    });

    // Helper function for typing indicator
    function addTypingIndicator() {
        const typing = document.createElement('div');
        typing.className = 'message typing-indicator';
        typing.innerHTML = '<i>shapes clay</i> <span class="typing-dots">...</span>';
        messageHistory.appendChild(typing);
        scrollToBottom();
        return typing;
    }
    
    function getUserId() {
        // Generate or retrieve a persistent user ID
        let userId = localStorage.getItem('adam_user_id');
        if (!userId) {
            userId = 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('adam_user_id', userId);
        }
        return userId;
    }
    
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
        }
        return fallbacks.default;
    }
    
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
});