// Workflow
const observer1 = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            // Select all workflow cards inside the observed container
            document.querySelectorAll('.workflow-card').forEach((card, index) => {
                setTimeout(() => {
                    card.classList.add('animate-workflow-card');
                }, index * 100);

            });

            observer1.unobserve(entry.target); // Stop observing after animation triggers
        }
    });
}, {
    threshold: 0.3// Trigger when 30% of the container is visible
});

observer1.observe(document.querySelector('.workflow-cards-container'));



// -------------------------------------------------------------------------------------------------------------------------------------------------------------

// Department 
const observer2 = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const departmentCards = document.querySelectorAll('.department-card');
            departmentCards.forEach((card, index) => {
                card.classList.add('animate-fade-in');
            });
            observer2.unobserve(entry.target); // Stop observing once animation is triggered
        }
    });
}, {
    threshold: 0.5 // Trigger when at least 50% of the element is visible
});

// Start observing the department-list section
observer2.observe(document.getElementById('department-list'));


// -------------------------------------------------------------------------------------------------------------------------------------------------------------

// Doctor Data
const doctors = Data.Doctors;


// Variables
let currentIndex = 0;
let cardsToShow = window.innerWidth < 768 ? 1 : window.innerWidth < 1024 ? 2 : 3;

// DOM Elements
const carousel = document.getElementById('doctorCarousel');
const paginationContainer = document.getElementById('paginationDots');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

// Initialize the carousel
function initCarousel() {
    // Clear the carousel
    carousel.innerHTML = '';

    // Create all doctor cards but only show the current ones
    doctors.forEach((doctor, index) => {
        const isVisible = index >= currentIndex && index < currentIndex + cardsToShow;

        const card = document.createElement('div');
        card.className = `doctor-card bg-white p-4 rounded-lg shadow-md mx-2 flex-shrink-0 ${isVisible ? 'animate-left_movement' : 'hidden'}`;
        card.style.width = `calc(${100 / cardsToShow}% - 1rem)`;
        card.style.animationDelay = `${(index - currentIndex) * 0.1}s`;

        card.innerHTML = `
                    <div class="overflow-hidden rounded-lg">
                        <img src="${doctor.image}" alt="${doctor.name}" class="w-full object-cover aspect-[3/4] hover:scale-105 transition-transform duration-500">
                    </div>
                    <div class="text-center mt-4">
                        <h3 class="text-xl font-semibold text-gray-800">${doctor.name}</h3>
                        <p class="text-blue-500">${doctor.specialty}</p>
                    </div>
                `;
        carousel.appendChild(card);
    });

    // Update pagination dots
    updatePagination();
}

// Update pagination dots
function updatePagination() {
    paginationContainer.innerHTML = '';

    const totalDots = Math.ceil((doctors.length - cardsToShow + 1) / 1);

    for (let i = 0; i < totalDots; i++) {
        const dot = document.createElement('button');
        dot.className = `pagination-dot h-2 rounded-full  transition-all ${currentIndex === i ? 'w-8 bg-blue-500 active' : 'w-2 bg-gray-300'}`;
        dot.setAttribute('aria-label', `Go to slide ${i + 1}`);
        dot.addEventListener('click', () => { 
            currentIndex = i;
            initCarousel();
        }); 

        paginationContainer.appendChild(dot);
    }
}

// Event listeners for navigation buttons
prevBtn.addEventListener('click', () => {
    if (currentIndex > 0) {
        currentIndex--;
        initCarousel();
    }
});

nextBtn.addEventListener('click', () => {
    if (currentIndex < doctors.length - cardsToShow) {
        currentIndex++;
        initCarousel();
    }
});

// Handle window resize
window.addEventListener('resize', () => {
    const newCardsToShow = window.innerWidth < 768 ? 1 : window.innerWidth < 1024 ? 2 : 3;
    if (newCardsToShow !== cardsToShow) {
        cardsToShow = newCardsToShow;
        // Adjust currentIndex if necessary
        if (currentIndex > doctors.length - cardsToShow) {
            currentIndex = doctors.length - cardsToShow;
        }
        initCarousel();
    }
});

// Auto-switch functionality
let autoplayInterval;

function startAutoplay() {
    autoplayInterval = setInterval(() => {
        if (currentIndex < doctors.length - cardsToShow) {
            currentIndex++;
        } else {
            currentIndex = 0;
        }
        initCarousel();
    }, 5000); // Change slide every 5 seconds
}

function stopAutoplay() {
    clearInterval(autoplayInterval);
}

// Pause autoplay on hover
carousel.addEventListener('mouseenter', stopAutoplay);
carousel.addEventListener('mouseleave', startAutoplay);

// Initialize the carousel and start autoplay
initCarousel();
startAutoplay();








// -------------------------------------------------------------------------------------------------------------------------------------------------------------

// Testomonial Data 

const Full_star = `<svg id='Rating_Star_24' width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><rect width='24' height='24' stroke='none' fill='#000000' opacity='0'/> <g transform="matrix(0.83 0 0 0.83 12 12)" > <g style="" > <g transform="matrix(1 0 0 1 0 0)" > <path style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-dashoffset: 0; stroke-linejoin: miter; stroke-miterlimit: 4; fill: rgb(255,239,94); fill-rule: nonzero; opacity: 1;" transform=" translate(-12, -12)" d="M 11.533 1.57101 C 11.5688 1.47582 11.6328 1.3938 11.7164 1.33591 C 11.8 1.27802 11.8993 1.24701 12.001 1.24701 C 12.1027 1.24701 12.202 1.27802 12.2856 1.33591 C 12.3692 1.3938 12.4332 1.47582 12.469 1.57101 L 15 8.74701 L 22.148 8.74701 C 22.2502 8.747 22.35 8.77832 22.4339 8.83675 C 22.5177 8.89518 22.5817 8.9779 22.6171 9.07379 C 22.6525 9.16967 22.6577 9.2741 22.6319 9.37302 C 22.6061 9.47193 22.5507 9.56058 22.473 9.62701 L 16.5 14.579 L 19 22.089 C 19.0334 22.1896 19.034 22.2983 19.0017 22.3993 C 18.9693 22.5003 18.9057 22.5884 18.8199 22.6508 C 18.7342 22.7132 18.6309 22.7468 18.5248 22.7467 C 18.4188 22.7465 18.3155 22.7127 18.23 22.65 L 12 18.079 L 5.76701 22.65 C 5.6814 22.7115 5.57858 22.7443 5.47321 22.7438 C 5.36783 22.7434 5.26531 22.7096 5.18025 22.6474 C 5.0952 22.5852 5.03198 22.4977 4.99961 22.3974 C 4.96724 22.2971 4.96738 22.1892 5.00001 22.089 L 7.50001 14.579 L 1.52601 9.62701 C 1.44832 9.56058 1.39287 9.47193 1.36711 9.37302 C 1.34135 9.2741 1.34652 9.16967 1.38193 9.07379 C 1.41734 8.9779 1.48129 8.89518 1.56516 8.83675 C 1.64903 8.77832 1.74879 8.747 1.85101 8.74701 L 9.00001 8.74701 L 11.533 1.57101 Z" stroke-linecap="round" /> </g> <g transform="matrix(1 0 0 1 -5.32 0)" > <path style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-dashoffset: 0; stroke-linejoin: miter; stroke-miterlimit: 4; fill: rgb(255,249,191); fill-rule: nonzero; opacity: 1;" transform=" translate(-6.68, -12)" d="M 12 18.079 L 5.76701 22.65 C 5.6814 22.7115 5.57858 22.7443 5.47321 22.7438 C 5.36783 22.7434 5.26531 22.7096 5.18025 22.6474 C 5.0952 22.5852 5.03198 22.4977 4.99961 22.3974 C 4.96724 22.2971 4.96738 22.1892 5.00001 22.089 L 7.50001 14.579 L 1.52601 9.62701 C 1.44832 9.56058 1.39287 9.47193 1.36711 9.37302 C 1.34135 9.2741 1.34652 9.16967 1.38193 9.07379 C 1.41734 8.9779 1.48129 8.89518 1.56516 8.83675 C 1.64903 8.77832 1.74879 8.747 1.85101 8.74701 L 9.00001 8.74701 L 11.532 1.57101 C 11.5678 1.47582 11.6318 1.3938 11.7154 1.33591 C 11.799 1.27802 11.8983 1.24701 12 1.24701 L 12 18.079 Z" stroke-linecap="round" /> </g> <g transform="matrix(1 0 0 1 0 0)" > <path style="stroke: rgb(25,25,25); stroke-width: 1; stroke-dasharray: none; stroke-linecap: round; stroke-dashoffset: 0; stroke-linejoin: round; stroke-miterlimit: 4; fill: none; fill-rule: nonzero; opacity: 1;" transform=" translate(-12, -12)" d="M 11.533 1.57101 C 11.5688 1.47582 11.6328 1.3938 11.7164 1.33591 C 11.8 1.27802 11.8993 1.24701 12.001 1.24701 C 12.1027 1.24701 12.202 1.27802 12.2856 1.33591 C 12.3692 1.3938 12.4332 1.47582 12.469 1.57101 L 15 8.74701 L 22.148 8.74701 C 22.2502 8.747 22.35 8.77832 22.4339 8.83675 C 22.5177 8.89518 22.5817 8.9779 22.6171 9.07379 C 22.6525 9.16967 22.6577 9.2741 22.6319 9.37302 C 22.6061 9.47193 22.5507 9.56058 22.473 9.62701 L 16.5 14.579 L 19 22.089 C 19.0334 22.1896 19.034 22.2983 19.0017 22.3993 C 18.9693 22.5003 18.9057 22.5884 18.8199 22.6508 C 18.7342 22.7132 18.6309 22.7468 18.5248 22.7467 C 18.4188 22.7465 18.3155 22.7127 18.23 22.65 L 12 18.079 L 5.76701 22.65 C 5.6814 22.7115 5.57858 22.7443 5.47321 22.7438 C 5.36783 22.7434 5.26531 22.7096 5.18025 22.6474 C 5.0952 22.5852 5.03198 22.4977 4.99961 22.3974 C 4.96724 22.2971 4.96738 22.1892 5.00001 22.089 L 7.50001 14.579 L 1.52601 9.62701 C 1.44832 9.56058 1.39287 9.47193 1.36711 9.37302 C 1.34135 9.2741 1.34652 9.16967 1.38193 9.07379 C 1.41734 8.9779 1.48129 8.89518 1.56516 8.83675 C 1.64903 8.77832 1.74879 8.747 1.85101 8.74701 L 9.00001 8.74701 L 11.533 1.57101 Z" stroke-linecap="round" /> </g> </g> </g> </svg>`;
const Empty_star = `<svg id='Star_24' width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><rect width='24' height='24' stroke='none' fill='#000000' opacity='0'/> <g transform="matrix(0.4 0 0 0.4 12 12)" > <path style="stroke: none; stroke-width: 1; stroke-dasharray: none; stroke-linecap: butt; stroke-dashoffset: 0; stroke-linejoin: miter; stroke-miterlimit: 4; fill: rgb(0,0,0); fill-rule: nonzero; opacity: 1;" transform=" translate(-25, -24.8)" d="M 25 1 C 24.587448437819113 1.0003573899416984 24.21745171913152 1.2540028470630233 24.068359 1.638671900000001 L 17.902344 17.535156 L 0.94921875 18.400391 C 0.5361244089496604 18.421301271604477 0.1785245802706652 18.694352310895226 0.04954463953851285 19.08735148259298 C -0.07943530119363951 19.480350654290728 0.04682045204112695 19.912200156205603 0.36718749999999956 20.173828 L 13.568359 30.966797 L 9.2324219 47.34375 C 9.12646962864894 47.742800908399424 9.276630584445037 48.1659432996735 9.610426980225581 48.40894016686066 C 9.944223376006123 48.65193703404781 10.393034545033865 48.66483395207868 10.740234 48.441406 L 25 39.289062 L 39.259766 48.441406 C 39.60696545264548 48.66483388017553 40.055776569605634 48.651936924345584 40.38957292468266 48.408940070673886 C 40.72336927975969 48.16594321700219 40.873530228824 47.742800877413245 40.767578 47.34375 L 36.431641 30.966797 L 49.632812 20.173828 C 49.95317902219769 19.912200187302915 50.079434793103644 19.480350742069874 49.950454914740824 19.087351591605163 C 49.821475036378004 18.69435244114045 49.46387529654981 18.421301366962094 49.050781 18.400391 L 32.097656 17.535156 L 25.931641 1.6386719 C 25.782548280868475 1.2540028470630227 25.412551562180887 1.0003573899416978 25 1 z M 25 4.7636719 L 30.466797 18.861328 C 30.60968898779115 19.229141631031354 30.955496183370457 19.478551484728474 31.349609 19.498047 L 46.359375 20.265625 L 34.667969 29.826172 C 34.36460539586974 30.074211371141768 34.23404925803034 30.47656788718194 34.333984 30.855469 L 38.175781 45.369141 L 25.541016 37.257812 C 25.211478939746424 37.04585360168865 24.788521060253576 37.04585360168865 24.458984 37.257812 L 11.824219 45.369141 L 15.666016 30.855469 C 15.765950741969661 30.47656788718194 15.635394604130266 30.074211371141768 15.332031 29.826172 L 3.640625 20.265625 L 18.650391 19.498047 C 19.044503816629543 19.478551484728474 19.39031101220885 19.229141631031354 19.533203 18.861328 L 25 4.7636719 z" stroke-linecap="round" /> </g> </svg>`;
const Half_star = `<svg id='Rating_Half_Star_24' width='24' height='24' viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink'><rect width='24' height='24' stroke='none' fill='#000000' opacity='0'/> <g transform="matrix(0.93 0 0 0.93 12 12)" > <path style="stroke: rgb(25,25,25); stroke-width: 1; stroke-dasharray: none; stroke-linecap: round; stroke-dashoffset: 0; stroke-linejoin: round; stroke-miterlimit: 4; fill: rgb(255,239,94); fill-rule: nonzero; opacity: 1;" transform=" translate(-12, -12)" d="M 17.559 18.079 L 10.859 22.65 C 10.7735 22.7127 10.6702 22.7465 10.5642 22.7467 C 10.4581 22.7468 10.3548 22.7132 10.2691 22.6508 C 10.1834 22.5884 10.1197 22.5003 10.0873 22.3993 C 10.055 22.2983 10.0556 22.1896 10.089 22.089 L 12.589 14.579 L 6.616 9.62701 C 6.53832 9.56058 6.48286 9.47193 6.4571 9.37302 C 6.43134 9.2741 6.43652 9.16967 6.47193 9.07379 C 6.50734 8.9779 6.57129 8.89518 6.65516 8.83675 C 6.73903 8.77832 6.83879 8.747 6.941 8.74701 L 14.091 8.74701 L 16.623 1.57101 C 16.6588 1.47582 16.7228 1.3938 16.8064 1.33591 C 16.89 1.27802 16.9893 1.24701 17.091 1.24701 C 17.1927 1.24701 17.292 1.27802 17.3756 1.33591 C 17.4592 1.3938 17.5232 1.47582 17.559 1.57101 L 17.559 18.079 Z" stroke-linecap="round" /> </g> </svg>`;



document.addEventListener('DOMContentLoaded', function () {
    // Testimonial Data 
    testimonials_DATA = Data.Testimonials;

    // Get DOM elements
    const testimonialWrapper = document.getElementById('testimonial-wrapper');
    const paginationDots = document.getElementById('pagination-dots');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    // Variables for slider functionality
    let currentIndex = 0;
    let cardsToShow = getCardsToShow();
    let autoSlideInterval;

    // Function to determine how many cards to show based on screen width
    function getCardsToShow() {
        if (window.innerWidth < 768) {
            return 1; // Mobile: 1 card
        } else if (window.innerWidth < 1024) {
            return 3; // Tablet: 3 cards
        } else if (window.innerWidth < 1280) {
            return 4; // Small desktop: 4 cards
        } else {
            return 5; // Large desktop: 5 cards
        }
    }

    function createStars(rating){
        // Generate star ratings dynamically
            let starsHTML = '';
            const roundedRating = Math.round(rating * 2) / 2; // Round to nearest 0.5
            const fullStars = Math.floor(roundedRating);
            const hasHalfStar = roundedRating % 1 !== 0;
            
            // Add full stars
            for (let i = 0; i < fullStars; i++) {
                starsHTML += Full_star;
            }
            
            // Add half star if needed
            if (hasHalfStar) {
                starsHTML += Half_star;
            }
            
            // Add empty stars
            const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
            for (let i = 0; i < emptyStars; i++) {
                starsHTML += Empty_star;
            }
            return starsHTML;
    }

    // Create testimonial slides
    function createSlides() {
        testimonialWrapper.innerHTML = '';

        testimonials_DATA.forEach((testimonial, index) => {
            const slide = document.createElement('div');
            slide.className = `testimonial-slide transition-all duration-300 px-2 md:px-3 ${getSlideWidthClass()}`;
            slide.setAttribute('data-index', index);

            starsHTML = createStars(testimonial.rating);

            slide.innerHTML = `
                <div class="bg-white rounded-lg shadow-md p-4 md:p-6 h-full transform transition-transform duration-300 hover:scale-105">
                    <div class="flex flex-col items-center">
                        <div class="w-16 h-16 md:w-24 md:h-24 rounded-full overflow-hidden mb-3 md:mb-4 border-2 border-blue-100">
                            <img src="${testimonial.image}" alt="${testimonial.name}" class="w-full h-full object-cover">
                        </div>
                        <h3 class="text-blue-500 text-lg md:text-xl font-semibold">${testimonial.name}</h3>
                        <div class="flex mt-2 mb-2 md:mb-3 ">
                            ${starsHTML}
                        </div>
                        <p class="text-center text-gray-600 text-sm md:text-base">${testimonial.feedback}</p>
                    </div>
                </div>
            `;
            testimonialWrapper.appendChild(slide);
        });
    }

    // Get appropriate slide width class based on screen size and cards to show
    function getSlideWidthClass() {
        switch (cardsToShow) {
            case 1: return 'w-full flex-shrink-0';
            case 3: return 'w-1/3 flex-shrink-0';
            case 4: return 'w-1/4 flex-shrink-0';
            case 5: return 'w-1/5 flex-shrink-0';
            default: return 'w-full flex-shrink-0';
        }
    }

    // Create pagination dots
    function createPaginationDots() {
        paginationDots.innerHTML = '';
        const totalSlides = testimonials_DATA.length;
        const totalPages = Math.max(1, totalSlides - cardsToShow + 1);

        for (let i = 0; i < totalPages; i++) {
            const dot = document.createElement('span');
            dot.className = `pagination-dot_testo h-2 w-6 md:w-8 ${i === 0 ? 'bg-blue-500' : 'bg-gray-300'} rounded-full mx-1 cursor-pointer transition-colors duration-300 hover:bg-blue-300`;
            dot.setAttribute('data-index', i);
            dot.addEventListener('click', () => {
                goToSlide(i);
            });
            paginationDots.appendChild(dot);
        }
    }

    // Update active pagination dot
    function updatePaginationDots() {
        const dots = document.querySelectorAll('.pagination-dot_testo');
        const totalSlides = testimonials_DATA.length;
        const totalPages = Math.max(1, totalSlides - cardsToShow + 1);

        if (dots.length === 0 || totalPages <= 1) return;

        dots.forEach((dot, index) => {

            if (index === currentIndex) {
                dot.classList.add('bg-blue-500');
                dot.classList.remove('bg-gray-300');
            } else {
                dot.classList.add('bg-gray-300');
                dot.classList.remove('bg-blue-500');
            }
        });
    }

    // Go to specific slide
    function goToSlide(index) {
        const totalSlides = testimonials_DATA.length;
        const maxIndex = Math.max(0, totalSlides - cardsToShow);
        currentIndex = Math.min(Math.max(0, index), maxIndex);
        updateSlider();
        resetAutoSlide();
    }

    // Go to next slide
    function nextSlide() {
        const totalSlides = testimonials_DATA.length;
        const maxIndex = Math.max(0, totalSlides - cardsToShow);
        currentIndex = (currentIndex >= maxIndex) ? 0 : currentIndex + 1;
        updateSlider();
        resetAutoSlide();
    }

    // Go to previous slide
    function prevSlide() {
        const totalSlides = testimonials_DATA.length;
        const maxIndex = Math.max(0, totalSlides - cardsToShow);
        currentIndex = (currentIndex <= 0) ? maxIndex : currentIndex - 1;
        updateSlider();
        resetAutoSlide();
    }

    // Update slider position
    function updateSlider() {
        const slideWidth = 100 / cardsToShow;
        testimonialWrapper.style.transform = `translateX(-${currentIndex * slideWidth}%)`;
        updatePaginationDots();

        // Update visibility for accessibility and visual effect
        const slides = document.querySelectorAll('.testimonial-slide');
        slides.forEach((slide, index) => {
            const slideIndex = parseInt(slide.getAttribute('data-index'));
            if (slideIndex >= currentIndex && slideIndex < currentIndex + cardsToShow) {
                slide.setAttribute('aria-hidden', 'false');
                slide.style.opacity = '1';
            } else {
                slide.setAttribute('aria-hidden', 'true');
                slide.style.opacity = '0.5';
            }
        });
    }

    // Reset auto slide timer
    function resetAutoSlide() {
        clearInterval(autoSlideInterval);
        startAutoSlide();
    }

    // Start auto sliding
    function startAutoSlide() {
        autoSlideInterval = setInterval(() => {
            nextSlide();
        }, 5000);
    }

    // Initialize slider
    function initSlider() {
        createSlides();
        createPaginationDots();
        updateSlider();
        startAutoSlide();

        // Add event listeners for navigation
        prevBtn.addEventListener('click', prevSlide);
        nextBtn.addEventListener('click', nextSlide);

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                prevSlide();
            } else if (e.key === 'ArrowRight') {
                nextSlide();
            }
        });

        // Animate stars
        animateStars();

        // Handle window resize
        window.addEventListener('resize', handleResize);

        // Add touch swipe support
        addTouchSupport();
    }

    // Animate star ratings
    function animateStars() {
        const starContainers = document.querySelectorAll('.star-animation');
        starContainers.forEach(container => {
            const stars = container.querySelectorAll('i');
            stars.forEach((star, index) => {
                star.style.animation = `fadeIn 0.5s ${index * 0.1}s forwards`;
                star.style.opacity = '0';
            });
        });
    }

    // Add touch swipe support
    function addTouchSupport() {
        let touchStartX = 0;
        let touchEndX = 0;

        testimonialWrapper.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        testimonialWrapper.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, { passive: true });

        function handleSwipe() {
            const minSwipeDistance = 50;
            if (touchEndX < touchStartX - minSwipeDistance) {
                nextSlide();
            }
            if (touchEndX > touchStartX + minSwipeDistance) {
                prevSlide();
            }
        }
    }

    // Handle window resize
    function handleResize() {
        const newCardsToShow = getCardsToShow();

        // Only rebuild if the number of visible cards has changed
        if (newCardsToShow !== cardsToShow) {
            cardsToShow = newCardsToShow;

            // Adjust current slide position
            const totalSlides = testimonials_DATA.length;
            const maxIndex = Math.max(0, totalSlides - cardsToShow);
            currentIndex = Math.min(currentIndex, maxIndex);

            // Rebuild slider components
            createSlides();
            createPaginationDots();
            updateSlider();
        }
    }

    // Initialize the slider
    initSlider();
});