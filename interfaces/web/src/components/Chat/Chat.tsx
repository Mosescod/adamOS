import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'adam';
  timestamp: Date;
  gesture?: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Sample Adam responses with clay gestures
  const adamResponses = [
    { 
      text: "Mercy flows like water through creation...", 
      gesture: "*softens clay*" 
    },
    { 
      text: "The Lord's compassion molds all things...", 
      gesture: "*shapes vessel*" 
    }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const userMsg: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    // Simulate API call
    setTimeout(() => {
      const response = adamResponses[Math.floor(Math.random() * adamResponses.length)];
      const adamMsg: Message = {
        id: Date.now().toString(),
        text: response.text,
        sender: 'adam',
        gesture: response.gesture,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, adamMsg]);
      setIsTyping(false);
    }, 1500);
  };

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-[70vh] bg-gray-800/50 rounded-lg border border-gray-700 overflow-hidden">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-3/4 rounded-lg p-3 ${
                message.sender === 'user' 
                  ? 'bg-cyan-500/10 border border-cyan-500/20' 
                  : 'bg-gray-700/80 border border-gray-600'
              }`}>
                {message.gesture && (
                  <p className="text-xs text-cyan-300 mb-1">{message.gesture}</p>
                )}
                <p>{message.text}</p>
                <p className="text-xs mt-1 text-gray-400">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-700/80 rounded-lg p-3 border border-gray-600">
              <div className="flex space-x-1">
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce"></div>
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-700">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Adam about creation, mercy, or divine wisdom..."
            className="flex-1 bg-gray-700 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 text-white"
            disabled={isTyping}
          />
          <button
            type="submit"
            disabled={!input.trim() || isTyping}
            className="bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}