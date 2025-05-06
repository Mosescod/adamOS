document.addEventListener('DOMContentLoaded', () => {
    // Tab navigation
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
    
    // Copy button functionality
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', () => {
            const codeBlock = button.parentElement;
            const code = codeBlock.querySelector('pre').textContent;
            
            navigator.clipboard.writeText(code).then(() => {
                button.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    button.innerHTML = '<i class="fas fa-copy"></i>';
                }, 2000);
            });
        });
    });
});