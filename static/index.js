const menuToggle = document.querySelector('.toggle');
const showcase = document.querySelector('.showcase');

// Toggle menu visibility
menuToggle.addEventListener('click', () => {
  menuToggle.classList.toggle('active');
  showcase.classList.toggle('active');
});

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.querySelector('.search-form');
    const resultsContainer = document.querySelector('.results-container');

    if (!searchForm || !resultsContainer) {
        console.error('Required elements not found. Check your HTML classes.');
        return;
    }

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Show loading state
        resultsContainer.innerHTML = '<p class="loading">Searching...</p>';
        
        const location = document.querySelector('#location').value;
        
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ location: location }),
            });

            const data = await response.json();
            
            if (data.error) {
                resultsContainer.innerHTML = `<p class="error">${data.error}</p>`;
                return;
            }

            if ((!data.places || data.places.length === 0) && 
                (!data.dining || data.dining.length === 0)) {
                resultsContainer.innerHTML = `<p class="no-results">No results found for ${location}</p>`;
                return;
            }

            let html = '<div class="results-grid">';
            
            // Tourist Places Section
            html += '<div class="places-section">';
            html += '<h2>Tourist Places</h2>';
            html += '<div class="places-grid">';
            if (data.places && data.places.length > 0) {
                data.places.forEach(place => {
                    const rating = typeof place.rating === 'number' ? 
                        place.rating.toFixed(1) : 'N/A';
                    
                    html += `
                        <div class="place-card">
                            <h3>${sanitizeHTML(place.name || 'Unknown Place')}</h3>
                            <p><strong>Location:</strong> ${sanitizeHTML(place.location || 'Unknown Location')}</p>
                            <p class="rating"><strong>Rating:</strong> ${rating}/5</p>
                            <p class="review">${sanitizeHTML(place.sample_review || 'No review available')}</p>
                        </div>
                    `;
                });
            } else {
                html += '<p class="no-results">No tourist places found</p>';
            }
            html += '</div></div>';
            
            // Dining Spots Section
            html += '<div class="dining-section">';
            html += '<h2>Dining Spots</h2>';
            html += '<div class="dining-grid">';
            if (data.dining && data.dining.length > 0) {
                data.dining.forEach(spot => {
                    const rating = typeof spot.rating === 'number' ? 
                        spot.rating.toFixed(1) : 'N/A';
                    
                    html += `
                        <div class="place-card">
                            <h3>${sanitizeHTML(spot.name || 'Unknown Restaurant')}</h3>
                            <p><strong>Location:</strong> ${sanitizeHTML(spot.location || 'Unknown Location')}</p>
                            <p class="rating"><strong>Rating:</strong> ${rating}/5</p>
                            <p class="review">${sanitizeHTML(spot.sample_review || 'No review available')}</p>
                        </div>
                    `;
                });
            } else {
                html += '<p class="no-results">No dining spots found</p>';
            }
            html += '</div></div>';
            
            html += '</div>';
            resultsContainer.innerHTML = html;

        } catch (error) {
            console.error('Error fetching search results:', error);
            resultsContainer.innerHTML = `
                <p class="error">Error fetching search results. Please try again.</p>
            `;
        }
    });
});

// Helper function to sanitize HTML and prevent XSS
function sanitizeHTML(str) {
    if (typeof str !== 'string') return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}