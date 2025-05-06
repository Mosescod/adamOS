document.addEventListener('DOMContentLoaded', () => {
    const securityForm = document.getElementById('security-form');
    const securityLog = document.getElementById('security-log');
    
    securityForm.addEventListener('submit', (e) => {
        e.preventDefault();
        addLogEntry("Security query initiated...");
        
        setTimeout(() => {
            addLogEntry("Query completed. No issues found.");
        }, 1500);
    });
    
    function addLogEntry(message) {
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.textContent = `> ${message}`;
        securityLog.appendChild(entry);
        securityLog.scrollTop = securityLog.scrollHeight;
    }
    
    // Simulate periodic status updates
    setInterval(() => {
        const messages = [
            "System check completed",
            "Memory scan clean",
            "Ethical protocols verified"
        ];
        const randomMessage = messages[Math.floor(Math.random() * messages.length)];
        addLogEntry(randomMessage);
    }, 10000);
});