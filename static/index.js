const menuToggle = document.querySelector('.toggle');
const showcase = document.querySelector('.showcase');

// Toggle menu visibility
menuToggle.addEventListener('click', () => {
  menuToggle.classList.toggle('active');
  showcase.classList.toggle('active');
});

// Form submission event listener
document.getElementById('searchForm').addEventListener('submit', async (event) => {
  event.preventDefault(); // Prevent default form submission
  
  const location = document.getElementById('locationInput').value;

  // Send the location to the Flask backend
  const response = await fetch('/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ location }),
  });

  // Parse the JSON response
  const data = await response.json();

  // Display the recommended places and dining spots
  const cardContainer = document.getElementById('cardContainer');
  cardContainer.innerHTML = ''; // Clear previous results

  // Handle the places
  data.places.forEach(place => {
    const card = `
      <div class="card">
        <h3>${place.name}</h3>
        <p>${place.description}</p>
      </div>
    `;
    cardContainer.innerHTML += card;
  });

  // Handle the dining spots
  data.dining.forEach(spot => {
    const card = `
      <div class="card">
        <h3>${spot.name}</h3>
        <p>${spot.description}</p>
      </div>
    `;
    cardContainer.innerHTML += card;
  });
});
