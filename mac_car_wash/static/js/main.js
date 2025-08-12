// Enhanced 3D Car Animation using Three.js
let scene, camera, renderer, car, particles;

function init3D() {
    const canvas = document.getElementById('carCanvas');
    if (!canvas) return;

    // Scene setup
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, canvas.offsetWidth / canvas.offsetHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
    renderer.setClearColor(0x000000, 0);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    // Create car
    createCar();
    createParticles();
    setupLighting();
    
    camera.position.set(8, 4, 8);
    camera.lookAt(0, 0, 0);

    animate();
    setupEventListeners();
}

function createCar() {
    // Car body
    const bodyGeometry = new THREE.BoxGeometry(4, 1.2, 2);
    const bodyMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x3b82f6,
        shininess: 100
    });
    car = new THREE.Mesh(bodyGeometry, bodyMaterial);
    car.castShadow = true;
    scene.add(car);

    // Car details
    const roofGeometry = new THREE.BoxGeometry(3, 0.8, 1.8);
    const roofMaterial = new THREE.MeshPhongMaterial({ color: 0x2563eb });
    const roof = new THREE.Mesh(roofGeometry, roofMaterial);
    roof.position.y = 1;
    car.add(roof);

    // Wheels
    const wheelGeometry = new THREE.CylinderGeometry(0.4, 0.4, 0.2, 16);
    const wheelMaterial = new THREE.MeshPhongMaterial({ color: 0x1f2937 });
    
    const wheelPositions = [
        [-1.5, -0.7, 1.2], [1.5, -0.7, 1.2],
        [-1.5, -0.7, -1.2], [1.5, -0.7, -1.2]
    ];

    wheelPositions.forEach(pos => {
        const wheel = new THREE.Mesh(wheelGeometry, wheelMaterial);
        wheel.position.set(pos[0], pos[1], pos[2]);
        wheel.rotation.z = Math.PI / 2;
        wheel.castShadow = true;
        car.add(wheel);
    });
}

function createParticles() {
    // Water droplet particles
    const particleCount = 500;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 15;     // x
        positions[i + 1] = Math.random() * 10 + 5;     // y
        positions[i + 2] = (Math.random() - 0.5) * 15; // z
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const material = new THREE.PointsMaterial({
        color: 0x00bfff,
        size: 0.1,
        transparent: true,
        opacity: 0.6
    });

    particles = new THREE.Points(geometry, material);
    scene.add(particles);
}

function setupLighting() {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
    scene.add(ambientLight);

    // Directional light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    scene.add(directionalLight);
}

function animate() {
    requestAnimationFrame(animate);

    if (car) {
        car.rotation.y += 0.005;
    }

    if (particles) {
        const positions = particles.geometry.attributes.position.array;
        for (let i = 1; i < positions.length; i += 3) {
            positions[i] -= 0.02; // Move particles down
            if (positions[i] < -5) {
                positions[i] = 10; // Reset to top
            }
        }
        particles.geometry.attributes.position.needsUpdate = true;
    }

    renderer.render(scene, camera);
}

function setupEventListeners() {
    window.addEventListener('resize', onWindowResize);
}

function onWindowResize() {
    const canvas = document.getElementById('carCanvas');
    if (canvas && camera && renderer) {
        camera.aspect = canvas.offsetWidth / canvas.offsetHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);
    }
}

// Enhanced Contact Form Handler
document.addEventListener('DOMContentLoaded', function() {
    init3D();
    
    // Navigation scroll effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Contact form submission
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const btnText = submitBtn.querySelector('.submit-text');
            const btnLoader = submitBtn.querySelector('.btn-loader');
            
            // Show loading state
            btnText.classList.add('d-none');
            btnLoader.classList.remove('d-none');
            submitBtn.disabled = true;
            
            try {
                const formData = new FormData(this);
                const data = Object.fromEntries(formData);
                
                const response = await fetch('/api/contact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Show success modal
                    const modal = new bootstrap.Modal(document.getElementById('successModal'));
                    const bookingIdElement = document.getElementById('bookingId');
                    if (bookingIdElement) {
                        bookingIdElement.textContent = result.booking_id;
                    }
                    modal.show();
                    
                    // Reset form
                    this.reset();
                } else {
                    alert(result.message || 'Something went wrong. Please try again.');
                }
                
            } catch (error) {
                console.error('Error:', error);
                alert('Network error. Please try again or call us directly.');
            } finally {
                // Reset button state
                btnText.classList.remove('d-none');
                btnLoader.classList.add('d-none');
                submitBtn.disabled = false;
            }
        });
    }
});

// Book service function
function bookService(serviceKey, serviceName, price) {
    const serviceSelect = document.getElementById('service');
    const contactSection = document.getElementById('contact');
    
    if (serviceSelect) {
        serviceSelect.value = serviceKey;
    }
    
    if (contactSection) {
        contactSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Counter animation
function animateCounters() {
    const counters = document.querySelectorAll('[data-count]');
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-count'));
        const increment = target / 200;
        let current = 0;
        
        const updateCounter = () => {
            if (current < target) {
                current += increment;
                counter.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        updateCounter();
    });
}

// Initialize counter animation when visible
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            animateCounters();
            observer.unobserve(entry.target);
        }
    });
});

const statsSection = document.querySelector('.hero-stats');
if (statsSection) {
    observer.observe(statsSection);
}
