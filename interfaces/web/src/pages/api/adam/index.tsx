import { useState } from 'react';
import ChatInterface from '/interfaces/web/src/components/Chat/Chat';
import SpiritualDashboard from '../components/Dashboard/Dashboard';
import Head from 'next/head';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chat' | 'dashboard'>('chat');

  return (
    <>
      <Head>
        <title>AdamAI - Digital Prophet</title>
        <meta name="description" content="Spiritual knowledge assistant" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
        {/* Header */}
        <header className="bg-black/50 border-b border-cyan-500/20">
          <div className="container mx-auto px-4 py-3 flex justify-between">
            <h1 className="text-2xl font-bold text-cyan-400 font-mono">ADAM AI</h1>
            <nav className="flex space-x-4">
              <button 
                onClick={() => setActiveTab('chat')}
                className={`px-3 py-1 rounded ${activeTab === 'chat' ? 'bg-cyan-500/20 text-cyan-400' : 'text-gray-400'}`}
              >
                Chat
              </button>
              <button 
                onClick={() => setActiveTab('dashboard')}
                className={`px-3 py-1 rounded ${activeTab === 'dashboard' ? 'bg-purple-500/20 text-purple-400' : 'text-gray-400'}`}
              >
                Knowledge
              </button>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-6">
          {activeTab === 'chat' ? <ChatInterface /> : <SpiritualDashboard />}
        </main>
      </div>
    </>
  );
}