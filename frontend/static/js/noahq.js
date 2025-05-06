// noahq.js - Complete implementation
document.addEventListener('DOMContentLoaded', () => {
    const consoleOutput = document.getElementById('console-output');
    const noahqForm = document.getElementById('noahq-form');
    const queryType = document.getElementById('query-type');
    
    // Security console functionality
    const setupSecurityConsole = () => {
        displaySystemMessage("NOAH-Q SECURITY SUBSYSTEM INITIALIZED");
        displaySystemMessage("RUNNING DIAGNOSTICS...");
        displaySystemMessage("ALL SYSTEMS NOMINAL");
        displaySystemMessage("READY FOR SECURITY QUERIES");
        
        noahqForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const type = queryType.value;
            if (!type) {
                displayWarning("QUERY TYPE REQUIRED");
                return;
            }
            
            displaySystemMessage(`PROCESSING ${type.toUpperCase()} QUERY...`);
            
            // Simulate processing
            setTimeout(() => {
                const responses = {
                    security: "SECURITY ANALYSIS COMPLETE. NO CRITICAL VULNERABILITIES DETECTED.",
                    ethical: "ETHICAL REVIEW CONCLUDED. ALL SYSTEMS WITHIN ESTABLISHED PARAMETERS.",
                    system: "SYSTEM DIAGNOSTIC COMPLETE. ALL COMPONENTS FUNCTIONING OPTIMALLY."
                };
                
                displaySystemMessage(responses[type]);
            }, 2000);
        });
    };
    
    const displaySystemMessage = (text) => {
        const message = document.createElement('p');
        message.innerHTML = `&gt; ${text}`;
        consoleOutput.appendChild(message);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    };
    
    const displayWarning = (text) => {
        const warning = document.createElement('p');
        warning.className = 'warning';
        warning.innerHTML = `! ${text} !`;
        consoleOutput.appendChild(warning);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    };

    // Status monitoring
    const monitorStatus = () => {
        // Randomly change status lights for visual effect
        setInterval(() => {
            const lights = document.querySelectorAll('.status-light');
            lights.forEach(light => {
                if (Math.random() > 0.9) {
                    light.classList.toggle('status-alert');
                    light.classList.toggle('status-ok');
                }
            });
        }, 3000);
    };

    setupSecurityConsole();
    monitorStatus();
});