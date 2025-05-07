document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const securityLog = document.getElementById('security-log');
    const securityForm = document.getElementById('security-form');
    const refreshBtn = document.getElementById('refresh-btn');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    const clearLogBtn = document.getElementById('clear-log');
    const githubLink = document.getElementById('github-link');
    const logCounter = document.querySelector('.log-counter');
    const filterButtons = document.querySelectorAll('.filter-btn');
    const statusCards = {
        encryption: document.getElementById('encryption-status'),
        auth: document.getElementById('auth-status'),
        ethics: document.getElementById('ethics-status'),
        system: document.getElementById('system-status')
    };

    // State management
    const state = {
        logEntries: [],
        sessionId: 'session-' + Date.now(),
        activityCounters: {
            pageOpens: 0,
            adamInteractions: 0,
            githubClicks: 0,
            scansRun: 0
        },
        systemStatus: {
            encryption: true,
            authentication: true,
            ethics: true,
            system: true
        }
    };

    // Initialize console
    initSecurityConsole();

    // Event listeners
    securityForm.addEventListener('submit', handleScanRequest);
    refreshBtn.addEventListener('click', handleRefresh);
    fullscreenBtn.addEventListener('click', toggleFullscreen);
    clearLogBtn.addEventListener('click', clearLog);
    githubLink.addEventListener('click', handleGitHubClick);
    filterButtons.forEach(btn => btn.addEventListener('click', filterLogs));

    // Cross-tab communication for ADAM interactions
    window.addEventListener('storage', handleStorageEvent);

    // System monitoring
    const systemMonitor = setInterval(monitorSystem, 15000);

    // Initialize functions
    function initSecurityConsole() {
        state.activityCounters.pageOpens++;
        addLogEntry(`Security console initialized`, "success", `Session ID: ${state.sessionId}`);
        addLogEntry(`Establishing secure connection...`, "", "AES-256 handshake initiated");
        
        setTimeout(() => {
            addLogEntry(`Secure connection established`, "success", "TLS 1.3 with P-384 ECDHE");
            updateStatusCard('encryption', true);
        }, 800);

        setTimeout(() => {
            addLogEntry(`Authentication protocols engaged`, "success", "OAuth 2.0 with PKCE");
            updateStatusCard('auth', true);
        }, 1200);

        setTimeout(() => {
            addLogEntry(`Ethical constraints verified`, "success", "All protocols active");
            updateStatusCard('ethics', true);
            addLogEntry(`System ready`, "success", "All subsystems nominal");
            updateStatusCard('system', true);
        }, 1800);

        // Load any existing ADAM interactions from localStorage
        const adamData = localStorage.getItem('adam-interaction');
        if (adamData) {
            handleAdamInteraction(JSON.parse(adamData));
        }
    }

    function handleScanRequest(e) {
        e.preventDefault();
        state.activityCounters.scansRun++;
        
        const queryType = document.getElementById('query-type').value;
        const details = document.getElementById('query-details').value;
        const deepScan = securityForm.querySelector('[name="deep-scan"]').checked;
        const validateEthics = securityForm.querySelector('[name="validate-ethics"]').checked;

        addLogEntry(`Initiating ${queryType}`, "success", 
                   `Scan #${state.activityCounters.scansRun} | Deep scan: ${deepScan ? 'YES' : 'NO'}`);
        
        if (details) {
            addLogEntry(`Scan parameters: ${truncate(details, 60)}`, "", 
                       `Ethics validation: ${validateEthics ? 'ENABLED' : 'DISABLED'}`);
        }

        simulateSecurityScan(queryType, deepScan, validateEthics);
        securityForm.querySelector('textarea').value = '';
    }

    function simulateSecurityScan(type, deepScan, validateEthics) {
        const steps = {
            "Security Audit": [
                {msg: "Checking firewall configurations", delay: 800},
                {msg: "Scanning for vulnerabilities", delay: 1200, risk: 0.2},
                {msg: "Verifying encryption standards", delay: 1000},
                {msg: "Reviewing access logs", delay: 1500, risk: 0.3}
            ],
            "Ethical Review": [
                {msg: "Analyzing response patterns", delay: 1000},
                {msg: "Checking bias mitigation", delay: 1800, risk: 0.4},
                {msg: "Verifying truthfulness metrics", delay: 1200},
                {msg: "Reviewing ethical constraints", delay: 2000, risk: 0.2}
            ],
            "System Check": [
                {msg: "Testing memory allocation", delay: 800},
                {msg: "Checking processor load", delay: 1000, risk: 0.3},
                {msg: "Verifying network latency", delay: 600},
                {msg: "Reviewing subsystem status", delay: 1200}
            ],
            "Threat Scan": [
                {msg: "Initializing threat database", delay: 1500},
                {msg: "Scanning for known vulnerabilities", delay: 2000, risk: 0.5},
                {msg: "Checking for anomalous patterns", delay: 1800, risk: 0.4},
                {msg: "Verifying protection status", delay: 1200}
            ]
        };

        let totalDelay = 0;
        steps[type].forEach((step, index) => {
            totalDelay += step.delay;
            
            setTimeout(() => {
                const isWarning = step.risk && Math.random() < step.risk;
                const status = isWarning ? "warning" : "";
                const details = isWarning ? "Potential issue detected" : "";
                
                addLogEntry(step.msg, status, details);
                
                if (index === steps[type].length - 1) {
                    setTimeout(() => {
                        const scanSuccess = !isWarning || Math.random() > 0.5;
                        addLogEntry(
                            `${type} ${scanSuccess ? 'completed successfully' : 'completed with warnings'}`,
                            scanSuccess ? "success" : "warning",
                            scanSuccess ? "No critical issues found" : "Review recommended"
                        );
                    }, 500);
                }
            }, totalDelay);
        });
    }

    function handleRefresh() {
        refreshBtn.querySelector('i').classList.add('spin');
        addLogEntry("Manual refresh initiated", "success");
        
        setTimeout(() => {
            addLogEntry("System status refreshed", "success");
            refreshBtn.querySelector('i').classList.remove('spin');
            
            // Random status update
            if (Math.random() > 0.7) {
                const randomStatus = Math.random() > 0.8 ? "warning" : "success";
                const msg = randomStatus === "warning" 
                    ? "Minor system anomaly detected" 
                    : "All systems nominal";
                
                addLogEntry(msg, randomStatus);
            }
        }, 1000);
    }

    function handleGitHubClick(e) {
        e.preventDefault();
        state.activityCounters.githubClicks++;
        
        addLogEntry(
            `GitHub access requested`, 
            "warning", 
            `Attempt #${state.activityCounters.githubClicks} | Verification required`
        );
        
        // Simulate security verification
        setTimeout(() => {
            const verified = Math.random() > 0.1;
            
            if (verified) {
                addLogEntry(
                    "GitHub access verified", 
                    "success", 
                    "Credentials accepted. Redirecting..."
                );
                setTimeout(() => {
                    window.open(githubLink.href, '_blank');
                }, 500);
            } else {
                addLogEntry(
                    "GitHub access denied", 
                    "error", 
                    "Security verification failed"
                );
            }
        }, 1500);
    }

    function handleStorageEvent(e) {
        if (e.key === 'adam-interaction') {
            const data = JSON.parse(e.newValue);
            handleAdamInteraction(data);
        }
    }

    function handleAdamInteraction(data) {
        state.activityCounters.adamInteractions++;
        
        addLogEntry(
            `ADAM interaction detected`, 
            "success", 
            `Query: ${truncate(data.query, 40)}`
        );
        
        // Verify response integrity
        setTimeout(() => {
            const verified = Math.random() > 0.15;
            addLogEntry(
                `Response integrity ${verified ? 'verified' : 'flagged'}`,
                verified ? "success" : "warning",
                verified ? `Response ID: ${data.responseId}` : "Potential ethical concern detected"
            );
            
            if (!verified) {
                updateStatusCard('ethics', false);
            }
        }, 800);
    }

    function monitorSystem() {
        const checks = [
            { component: "encryption", risk: 0.05, msg: "Encryption pulse verification" },
            { component: "authentication", risk: 0.1, msg: "Auth token validation" },
            { component: "ethics", risk: 0.15, msg: "Ethical protocol audit" },
            { component: "system", risk: 0.2, msg: "System health check" }
        ];
        
        checks.forEach(check => {
            const isWarning = Math.random() < check.risk;
            
            if (isWarning) {
                addLogEntry(
                    check.msg,
                    "warning",
                    "Minor anomaly detected"
                );
                updateStatusCard(check.component, false);
                
                // Simulate auto-recovery
                setTimeout(() => {
                    if (Math.random() > 0.3) {
                        addLogEntry(
                            `${check.component} auto-recovery`,
                            "success",
                            "Issue resolved automatically"
                        );
                        updateStatusCard(check.component, true);
                    }
                }, 5000 + Math.random() * 5000);
            }
        });
    }

    function addLogEntry(message, type = "", details = "") {
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        
        const entry = {
            id: 'log-' + Date.now(),
            time: timeString,
            message,
            type,
            details,
            timestamp: now.getTime()
        };
        
        state.logEntries.push(entry);
        renderLogEntry(entry);
        updateLogCounter();
        
        // Keep log from growing infinitely
        if (state.logEntries.length > 200) {
            const removed = state.logEntries.shift();
            document.getElementById(removed.id)?.remove();
        }
    }

    function renderLogEntry(entry) {
        const element = document.createElement('div');
        element.className = `log-entry ${entry.type}`;
        element.id = entry.id;
        
        element.innerHTML = `
            <div class="entry-time">${entry.time}</div>
            <div class="entry-message">
                ${entry.message}
                ${entry.details ? `<div class="entry-details">${entry.details}</div>` : ''}
            </div>
        `;
        
        securityLog.appendChild(element);
        securityLog.scrollTop = securityLog.scrollHeight;
    }

    function filterLogs(e) {
        const filter = e.target.dataset.filter;
        
        filterButtons.forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        
        securityLog.innerHTML = '';
        
        const filtered = filter === 'all' 
            ? state.logEntries 
            : state.logEntries.filter(entry => entry.type === filter);
        
        filtered.forEach(renderLogEntry);
        updateLogCounter(filtered.length);
    }

    function updateLogCounter(count = state.logEntries.length) {
        logCounter.textContent = `${count} ${count === 1 ? 'entry' : 'entries'}`;
    }

    function updateStatusCard(component, status) {
        state.systemStatus[component] = status;
        const card = statusCards[component];
        
        if (!card) return;
        
        const icon = card.querySelector('.status-icon');
        const statusText = card.querySelector('.status-info p');
        
        if (status) {
            icon.className = 'status-icon success';
            icon.innerHTML = `<i class="fas fa-check"></i>`;
            statusText.textContent = statusText.textContent.replace(/⚠️|❌/, '') + ' ✅';
        } else {
            icon.className = 'status-icon warning';
            icon.innerHTML = `<i class="fas fa-exclamation-triangle"></i>`;
            statusText.textContent = statusText.textContent.replace(/✅|❌/, '') + ' ⚠️';
            
            // 20% chance to escalate to error
            if (Math.random() > 0.8) {
                setTimeout(() => {
                    icon.className = 'status-icon error';
                    icon.innerHTML = `<i class="fas fa-times"></i>`;
                    statusText.textContent = statusText.textContent.replace(/⚠️|✅/, '') + ' ❌';
                }, 2000);
            }
        }
    }

    function toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen()
                .then(() => {
                    fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>';
                    addLogEntry("Entered fullscreen mode", "success");
                })
                .catch(err => {
                    addLogEntry(`Fullscreen error: ${err.message}`, "error");
                });
        } else {
            document.exitFullscreen();
            fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
        }
    }

    function clearLog() {
        state.logEntries = [];
        securityLog.innerHTML = '';
        addLogEntry("Log cleared by operator", "success");
        updateLogCounter();
    }

    function truncate(str, n) {
        return str.length > n ? str.substring(0, n) + '...' : str;
    }

    // Cross-tab communication setup
    if (!window.adamSecurityListener) {
        window.adamSecurityListener = true;
        localStorage.setItem('noahq-active', Date.now());
    }
});