export default function SpiritualDashboard() 
{
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Knowledge Card */}
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <h3 className="text-lg font-medium mb-4 text-cyan-400">Sacred Knowledge</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Quranic Verses</span>
              <span className="font-mono">1,428</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Biblical References</span>
              <span className="font-mono">892</span>
            </div>
          </div>
        </div>
        
        {/* Mood Card */}
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <h3 className="text-lg font-medium mb-4 text-purple-400">Spiritual State</h3>
          <div className="h-40 flex items-center justify-center">
            <ClayMeter3D size={120} />
          </div>
        </div>
        
        {/* Activity Card */}
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <h3 className="text-lg font-medium mb-4 text-blue-400">Recent Dialogues</h3>
          <div className="space-y-2">
            {recentConversations.map((conv, i) => (
              <div key={i} className="text-sm p-2 hover:bg-gray-700/30 rounded-lg">
                <p className="truncate">{conv.query}</p>
                <p className="text-xs text-gray-400">{conv.time}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }