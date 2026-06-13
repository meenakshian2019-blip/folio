// Wait for DOM tree structural parse completion
document.addEventListener('DOMContentLoaded', () => {
    
    /* -----------------------------------------
       1. FEATURE: DARK MODE TOGGLE TRACKER
       ----------------------------------------- */
    const themeToggleBtn = document.getElementById('theme-toggle');
    const bodyElement = document.body;

    // Read stored client side state preferences
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        bodyElement.classList.add('dark');
        themeToggleBtn.textContent = '☀️';
    }

    // Toggle execution binding on pointer interactions
    themeToggleBtn.addEventListener('click', () => {
        bodyElement.classList.toggle('dark');
        
        if (bodyElement.classList.contains('dark')) {
            themeToggleBtn.textContent = '☀️';
            localStorage.setItem('theme', 'dark');
        } else {
            themeToggleBtn.textContent = '🌙';
            localStorage.setItem('theme', 'light');
        }
    });

    /* -----------------------------------------
       2. FEATURE: BACK TO TOP BUTTON LOGIC
       ----------------------------------------- */
    const backToTopBtn = document.getElementById('back-to-top');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    });

    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    /* -----------------------------------------
       3. FEATURE: SCROLL-REVEAL ELEMENT INTERSECTION LOGIC
       ----------------------------------------- */
    const elementsToReveal = document.querySelectorAll('.reveal');

    // Threshold execution limits
    const observerOptions = {
        root: null, // Relative matching within system viewport context
        threshold: 0.15, // Elements activate once 15% becomes visible
        rootMargin: '0px 0px -20px 0px'
    };

    const revealIntersectionHandler = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                // Remove elements from active registry loops once rendered
                observer.unobserve(entry.target);
            }
        });
    };

    // Instantiate engine pipeline tracking structures
    const scrollRevealObserver = new IntersectionObserver(revealIntersectionHandler, observerOptions);

    // Bind element components onto the intersection registry matrix
    elementsToReveal.forEach(targetElement => {
        scrollRevealObserver.observe(targetElement);
    });
});

/* -----------------------------------------
       4.. FEATURE: FILTERABLE GALLERY MATRIX LOGIC
       ----------------------------------------- */
    const filterButtons = document.querySelectorAll('.filter-btn');
    const galleryItems = document.querySelectorAll('.gallery-item');
    const counterDisplay = document.getElementById('project-counter');

    // Functional engine updating live counter state strings
    const updateProjectCount = () => {
        const visibleItemsCount = document.querySelectorAll('.gallery-item:not(.hide-item)').length;
        const currentActiveFilter = document.querySelector('.filter-btn.active').textContent;
        
        if (currentActiveFilter === 'All') {
            counterDisplay.textContent = `Showing all ${visibleItemsCount} projects`;
        } else {
            counterDisplay.textContent = `Showing ${visibleItemsCount} ${currentActiveFilter} project${visibleItemsCount === 1 ? '' : 's'}`;
        }
    };

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active style classification from existing buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // Apply focus tracking context onto current clicked component
            button.classList.add('active');

            const selectionFilterTarget = button.getAttribute('data-filter');

            galleryItems.forEach(item => {
                const itemCategory = item.getAttribute('data-category');

                // Evaluate sorting visibility rules
                if (selectionFilterTarget === 'all' || selectionFilterTarget === itemCategory) {
                    item.classList.remove('hide-item');
                    // Add active back for scroll reveal engines if needed
                    item.classList.add('active'); 
                } else {
                    item.classList.add('hide-item');
                    item.classList.remove('active');
                }
            });

            // Re-render live calculation states
            updateProjectCount();
        });
    });

    // Initialize display layout count upon fresh browser load bindings
    updateProjectCount();

// Dynamic portfolio catalog injection loop module
async function renderGitHubProjects() {
    const sectionContainer = document.querySelector(".projects-grid"); // Match your HTML catalog parent ID node
    if(!sectionContainer) return;

    try {
        const response = await fetch("projects.json");
        const projects = await response.json();
        
        sectionContainer.innerHTML = ""; // Wipe default placeholders clean
        
        projects.forEach(project => {
            const card = document.createElement("div");
            card.className = "project-card"; // Match your custom styling grid class selectors
            card.innerHTML = `
                <h3>${project.name}</h3>
                <p>${project.description}</p>
                <div class="meta-metrics">
                    <span>Codebase: <strong>${project.language}</strong></span>
                    <span>⭐ ${project.stars}</span>
                </div>
                <a href="${project.html_url}" target="_blank" class="repo-link">Explore Codebase</a>
            `;
            sectionContainer.appendChild(card);
        });
    } catch (error) {
        console.error("Error loading dynamically generated repository catalog grid:", error);
    }
}

document.addEventListener("DOMContentLoaded", renderGitHubProjects);   