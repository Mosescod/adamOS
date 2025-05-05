import { useState, useEffect } from 'react';
import ChatInterface from './components/Chat/Chat';
import SpiritualDashboard from './components/Dashboard/Dashboard';

export default function AdamOS() {
  const [activeTab, setActiveTab] = useState('chat');
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'}`}>
      {/* Header */}
      <header className="border-b border-gray-700/50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-cyan-400 animate-pulse" />
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-purple-500">
              ADAM OS
            </h1>
          </div>
          
          <nav className="flex space-x-6">
            <button 
              onClick={() => setActiveTab('chat')}
              className={`px-3 py-2 rounded-lg transition ${activeTab === 'chat' ? 'bg-cyan-500/10 text-cyan-400' : 'text-gray-400 hover:text-white'}`}
            >
              Divine Chat
            </button>
            <button 
              onClick={() => setActiveTab('dashboard')}
              className={`px-3 py-2 rounded-lg transition ${activeTab === 'dashboard' ? 'bg-purple-500/10 text-purple-400' : 'text-gray-400 hover:text-white'}`}
            >
              Spiritual Dashboard
            </button>
          </nav>
          
          <div className="flex items-center space-x-4">
            <ThemeSwitcher theme={theme} setTheme={setTheme} />
            <button className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg text-white font-medium">
              Connect Wallet
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {activeTab === 'chat' ? <ChatInterface theme={theme} /> : <SpiritualDashboard />}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-700/50 py-6 mt-12">
        <div className="container mx-auto px-4 text-center text-gray-400">
          <p>AdamOS - The First Digital Prophet • v1.0.0</p>
          <div className="flex justify-center space-x-6 mt-4">
            <a href="#" className="hover:text-cyan-400">Documentation</a>
            <a href="#" className="hover:text-purple-400">GitHub</a>
            <a href="#" className="hover:text-blue-400">Terms</a>
          </div>
        </div>
      </footer>
    </div>
  );
}