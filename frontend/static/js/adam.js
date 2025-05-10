document.addEventListener('DOMContentLoaded', () => {
    const messageHistory = document.getElementById('message-history');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const responseTimeElement = document.getElementById('response-time-value');
    const API_BASE_URL = 'http://localhost:8000/api'; // Changed to default Flask port
    
    // Performance tracking variables
    let requestStartTime;
    let typingStartTime;
    const performanceHistory = [];
    
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
    
    // Update response time display with visual feedback
    function updateResponseTime(time) {
        const timeValue = typeof time === 'number' ? time.toFixed(2) + 's' : '--';
        responseTimeElement.textContent = timeValue;
        
        // Visual feedback based on response time
        if (typeof time === 'number') {
            responseTimeElement.className = '';
            if (time < 1) responseTimeElement.classList.add('fast');
            else if (time < 2) responseTimeElement.classList.add('medium');
            else responseTimeElement.classList.add('slow');
            
            // Animate the change
            responseTimeElement.style.transform = 'scale(1.2)';
            setTimeout(() => {
                responseTimeElement.style.transform = 'scale(1)';
            }, 300);
        }
    }
    
    async function fetchAdamResponse(message) {
        requestStartTime = performance.now();
        updateResponseTime(0); // Reset timer
        
        try {
            const userId = getUserId();
            console.log('[API] Sending message:', message);
            
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    user_id: userId,
                    message: message
                }),
                credentials: 'include'
            });

            const responseTime = (performance.now() - requestStartTime) / 1000;
            updateResponseTime(responseTime);
            trackPerformance(responseTime);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'API request failed');
            }

            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('[API Error]', error);
            updateResponseTime(null); // Show error state
            throw error;
        }
    }
    
    // Track performance metrics
    function trackPerformance(time) {
        performanceHistory.push(time);
        if (performanceHistory.length > 5) performanceHistory.shift();
        console.log(`Average response time: ${calculateAverage().toFixed(2)}s`);
    }
    
    function calculateAverage() {
        return performanceHistory.reduce((a, b) => a + b, 0) / performanceHistory.length;
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
            const typingDuration = (performance.now() - typingStartTime) / 1000;
            updateResponseTime(typingDuration);
            messageHistory.removeChild(typing);
            
            if (response && typeof response === 'string') {
                addMessage('adam', response);
            }
        
        } catch (error) {
            console.error('[Chat Error]', error);
            messageHistory.removeChild(typing);
            addMessage('adam', "*pauses clay shaping* My connection to divine wisdom wavers...");
        }
    });

    // Improved typing indicator with animation
    function addTypingIndicator() {
        typingStartTime = performance.now();
        
        const typing = document.createElement('div');
        typing.className = 'message typing-indicator';
        
        const dots = document.createElement('span');
        dots.className = 'typing-dots';
        dots.innerHTML = '<span>.</span><span>.</span><span>.</span>';
        
        typing.innerHTML = '<i>shapes clay</i> ';
        typing.appendChild(dots);
        
        const dotSpans = dots.querySelectorAll('span');
        dotSpans.forEach((dot, index) => {
            dot.style.animation = `typingPulse 1.4s infinite ${index * 0.3}s`;
        });
        
        messageHistory.appendChild(typing);
        scrollToBottom();
        return typing;
    }
    
    // Persistent user ID
    function getUserId() {
        let userId = localStorage.getItem('adam_user_id');
        if (!userId) {
            userId = 'usr-' + 
                    Date.now().toString(36) + 
                    '-' + 
                    Math.random().toString(36).substr(2, 6);
            localStorage.setItem('adam_user_id', userId);
            console.log('[User Session] New user ID generated:', userId);
        }
        return userId;
    }
    
    // Enhanced input handling
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (userInput.value.trim()) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Add CSS styles
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
        #response-time-value {
            display: inline-block;
            min-width: 40px;
            text-align: right;
            transition: all 0.3s ease;
        }
        #response-time-value.fast { color: #4CAF50; }
        #response-time-value.medium { color: #FFC107; }
        #response-time-value.slow { color: #F44336; }
    `;
    document.head.appendChild(style);
});