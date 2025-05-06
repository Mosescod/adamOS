// docs.js - Complete implementation
document.addEventListener('DOMContentLoaded', () => {
    // Tab navigation
    const setupTabs = () => {
        const navItems = document.querySelectorAll('.nav-item');
        const sections = document.querySelectorAll('.docs-section');
        
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                // Remove active class from all items
                navItems.forEach(navItem => navItem.classList.remove('active'));
                
                // Add active class to clicked item
                item.classList.add('active');
                
                // Hide all sections
                sections.forEach(section => {
                    section.style.display = 'none';
                });
                
                // Show selected section
                const target = item.getAttribute('data-target');
                document.getElementById(target).style.display = 'block';
            });
        });
    };

    // Animated code blocks
    const animateCodeBlocks = () => {
        const codeBlocks = document.querySelectorAll('.code-block');
        
        codeBlocks.forEach(block => {
            // Add line numbers
            const code = block.textContent.trim();
            const lines = code.split('\n');
            
            // Clear and reformat with line numbers
            block.innerHTML = '';
            
            lines.forEach((line, i) => {
                const lineElement = document.createElement('div');
                lineElement.className = 'code-line';
                
                const lineNumber = document.createElement('span');
                lineNumber.className = 'line-number';
                lineNumber.textContent = (i + 1).toString().padStart(2, ' ');
                
                const lineContent = document.createElement('span');
                lineContent.className = 'line-content';
                lineContent.textContent = line;
                
                lineElement.appendChild(lineNumber);
                lineElement.appendChild(lineContent);
                block.appendChild(lineElement);
            });
            
            // Add copy button
            const copyButton = document.createElement('button');
            copyButton.className = 'copy-btn';
            copyButton.innerHTML = '<i class="fas fa-copy"></i>';
            copyButton.title = 'Copy to clipboard';
            block.appendChild(copyButton);
            
            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(code)
                    .then(() => {
                        copyButton.innerHTML = '<i class="fas fa-check"></i>';
                        setTimeout(() => {
                            copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                        }, 2000);
                    });
            });
        });
    };

    setupTabs();
    animateCodeBlocks();
});