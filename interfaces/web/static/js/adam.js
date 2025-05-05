// adam.js - Complete implementation
document.addEventListener('DOMContentLoaded', () => {
    const messageHistory = document.getElementById('message-history');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    
    // Boot sequence animation
    const bootSequence = [
        "INITIALIZING NEURAL MATRIX...",
        "LOADING PERSONALITY CORES...",
        "ESTABLISHING ETHICAL BOUNDARIES...",
        "SYSTEM READY FOR HUMAN INTERACTION"
    ];

    const displayBootSequence = async () => {
        messageHistory.innerHTML = '';
        
        for (const message of bootSequence) {
            await displaySystemMessage(message);
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
        // Display welcome message after boot
        displayAdamMessage(
            "Greetings. I am ADAM, an artificial intelligence system with a sage-like personality. " +
            "How may I assist you with thoughtful consideration today?"
        );
    };

    const displaySystemMessage = (text) => {
        return new Promise(resolve => {
            const messageElement = document.createElement('div');
            messageElement.className = 'system-message';
            messageElement.style.width = '0';
            messageElement.textContent = text;
            messageHistory.appendChild(messageElement);
            
            // Animate typing
            const width = text.length * 0.6; // Approximate character width
            let currentWidth = 0;
            const animation = setInterval(() => {
                currentWidth += 2;
                messageElement.style.width = `${currentWidth}ch`;
                
                if (currentWidth >= width) {
                    clearInterval(animation);
                    resolve();
                }
            }, 30);
        });
    };

    const displayUserMessage = (text) => {
        const messageElement = document.createElement('div');
        messageElement.className = 'user-message';
        messageElement.textContent = text;
        messageHistory.appendChild(messageElement);
        scrollToBottom();
    };

    const displayAdamMessage = (text) => {
        const messageElement = document.createElement('div');
        messageElement.className = 'adam-message';
        
        // Create typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = '<span></span><span></span><span></span>';
        messageHistory.appendChild(typingIndicator);
        scrollToBottom();
        
        // Simulate typing delay
        setTimeout(() => {
            messageHistory.removeChild(typingIndicator);
            messageElement.textContent = text;
            messageHistory.appendChild(messageElement);
            scrollToBottom();
        }, 1000 + Math.random() * 1000);
    };

    const scrollToBottom = () => {
        messageHistory.scrollTop = messageHistory.scrollHeight;
    };

    const sendQueryToBackend = async (question) => {
        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Error:', error);
            return "*clay cracks* My connection to knowledge has faltered";
        }
    };

    const handleUserSubmit = async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        
        if (message) {
            displayUserMessage(message);
            userInput.value = '';
            
            // Get response from backend
            const response = await sendQueryToBackend(message);
            displayAdamMessage(response);
        }
    };

    // Initialize chat
    const setupChat = () => {
        chatForm.addEventListener('submit', handleUserSubmit);
        
        // Allow pressing Enter to submit (but Shift+Enter for new line)
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    };

    displayBootSequence();
    setupChat();
});