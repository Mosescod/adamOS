document.addEventListener('DOMContentLoaded', () => {
    const messageHistory = document.getElementById('message-history');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const API_BASE_URL = 'http://localhost:8000/api'; // Update if your API is hosted elsewhere
    
    // Adam's signature greeting
    setTimeout(() => {
        addMessage('adam', "*kneads clay* Greetings. I am Adam, the first of humankind. Ask me of creation, mercy, or the divine.");
    }, 500);
    
    // Enhanced message adding with animation
    function addMessage(sender, text) {
        const message = document.createElement('div');
        message.className = `message ${sender}-message`;
        
        // Process text formatting (italics between asterisks)
        const formattedText = text.replace(/\*(.*?)\*/g, '<i>$1</i>');
        message.innerHTML = formattedText;
        
        // Add with fade-in animation
        message.style.opacity = '0';
        messageHistory.appendChild(message);
        setTimeout(() => {
            message.style.transition = 'opacity 0.3s ease';
            message.style.opacity = '1';
        }, 10);
        
        scrollToBottom();
    }
    
    function scrollToBottom() {
        messageHistory.scrollTop = messageHistory.scrollHeight;
    }
    
    // Improved API response handler
    async function fetchAdamResponse(message) {
        try {
            const userId = getUserId();
            console.log(`[API Request] User ${userId} sending:`, message);
            
            const response = await fetch(`${API_BASE_URL}/system/status`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    message: message
                })
            });

            console.log('[API Response] Status:', response.status);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('[API Response] Data:', data);
            
            if (data.status !== 'success') {
                throw new Error(data.message || 'Received unsuccessful response from server');
            }

            return data.response;
        } catch (error) {
            console.error('[API Error]', error);
            throw error; // Re-throw for handling in the UI
        }
    }

    // Enhanced chat form handler
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
    
        if (!message) return;

        // Add user message immediately
        addMessage('user', message);
        userInput.value = '';
        userInput.focus();
    
        // Show typing indicator
        const typing = addTypingIndicator();
    
        try {
            const response = await fetchAdamResponse(message);
            messageHistory.removeChild(typing);
            
            // Only display if we got a valid response
            if (response && typeof response === 'string') {
                addMessage('adam', response);
            }
            // No else case - we'll remain silent if no response
        
        } catch (error) {
            console.error('[Chat Error]', error);
            messageHistory.removeChild(typing);
            
            // Show error to user in a subtle way
            addMessage('adam', "*pauses clay shaping* My connection to divine wisdom wavers...");
        }
    });

    // Improved typing indicator with animation
    function addTypingIndicator() {
        const typing = document.createElement('div');
        typing.className = 'message typing-indicator';
        
        // Create animated dots
        const dots = document.createElement('span');
        dots.className = 'typing-dots';
        dots.innerHTML = '<span>.</span><span>.</span><span>.</span>';
        
        typing.innerHTML = '<i>shapes clay</i> ';
        typing.appendChild(dots);
        
        // Add animation
        const dotSpans = dots.querySelectorAll('span');
        dotSpans.forEach((dot, index) => {
            dot.style.animation = `typingPulse 1.4s infinite ${index * 0.3}s`;
        });
        
        messageHistory.appendChild(typing);
        scrollToBottom();
        return typing;
    }
    
    // Persistent user ID with better generation
    function getUserId() {
        let userId = localStorage.getItem('adam_user_id');
        if (!userId) {
            // More robust ID generation
            userId = 'usr-' + 
                    Date.now().toString(36) + 
                    '-' + 
                    Math.random().toString(36).substr(2, 6);
            localStorage.setItem('adam_user_id', userId);
            
            // Log new user session
            console.log('[User Session] New user ID generated:', userId);
        }
        return userId;
    }
    
    // Enhanced input handling
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            
            // Only submit if there's actual content
            if (userInput.value.trim()) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Add some CSS for our typing animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes typingPulse {
            0%, 60%, 100% { opacity: 0.4; }
            30% { opacity: 1; }
        }
        .typing-dots span {
            opacity: 0.4;
            font-weight: bold;
        }
    `;
    document.head.appendChild(style);
});