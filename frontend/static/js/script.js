
function initBackgroundEffects() {
    // Create particle effects
    const particlesContainer = document.getElementById('particles');
    const particleCount = 30;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
        // Random properties
        const size = Math.random() * 10 + 5;
        const posX = Math.random() * 100;
        const duration = Math.random() * 20 + 10;
        const delay = Math.random() * -20;
        
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.left = `${posX}%`;
        particle.style.animationDuration = `${duration}s`;
        particle.style.animationDelay = `${delay}s`;
        
        particlesContainer.appendChild(particle);
    }
    
    // Parallax background effect
    const background = document.getElementById('background');
    document.addEventListener('mousemove', (e) => {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;
        background.style.transform = `translate(-${x * 10}px, -${y * 10}px)`;
    });
    
    // Ensure music plays (may require user interaction on some browsers)
    document.addEventListener('click', () => {
        const music = document.getElementById('bg-music');
        if (music.paused) {
            music.play().catch(e => console.log('Autoplay prevented:', e));
        }
    }, { once: true });
}

// Initialize on pages that have these elements
if (document.getElementById('particles') && document.getElementById('background')) {
    document.addEventListener('DOMContentLoaded', initBackgroundEffects);
}