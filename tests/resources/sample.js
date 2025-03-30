// Sample JavaScript file for testing JavaScript Processor

// Global variables
const config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000,
  maxRetries: 3
};

// Function declaration
function fetchData(endpoint, options = {}) {
  const url = `${config.apiUrl}/${endpoint}`;
  let retries = 0;
  
  return new Promise((resolve, reject) => {
    const tryFetch = () => {
      console.log(`Fetching data from ${url}`);
      
      fetch(url, options)
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          console.log('Data fetched successfully');
          resolve(data);
        })
        .catch(error => {
          console.error('Error fetching data:', error);
          
          if (retries < config.maxRetries) {
            retries++;
            console.log(`Retrying (${retries}/${config.maxRetries})...`);
            setTimeout(tryFetch, 1000);
          } else {
            reject(error);
          }
        });
    };
    
    tryFetch();
  });
}

// Event listener
document.addEventListener('DOMContentLoaded', () => {
  const button = document.getElementById('fetch-button');
  
  if (button) {
    button.addEventListener('click', async () => {
      try {
        const result = await fetchData('users');
        displayResults(result);
      } catch (error) {
        showError(error.message);
      }
    });
  }
});

// Arrow function
const displayResults = (data) => {
  const container = document.getElementById('results');
  
  if (!container) {
    console.error('Results container not found');
    return;
  }
  
  container.innerHTML = '';
  
  data.forEach(item => {
    const element = document.createElement('div');
    element.className = 'result-item';
    element.textContent = item.name;
    container.appendChild(element);
  });
};

// Another function
function showError(message) {
  const errorContainer = document.getElementById('error');
  
  if (errorContainer) {
    errorContainer.textContent = `Error: ${message}`;
    errorContainer.style.display = 'block';
  }
}

// IIFE
(function() {
  console.log('Script initialized');
  
  // Inline comment for testing
  /* Multi-line comment
     for testing comment detection */
  
  // Nested functions
  function helperFunction() {
    return 'Helper function called';
  }
  
  // Unused variable for testing
  const unusedVar = 'This is not used';
})();

// Export for testing module detection
export { fetchData, displayResults, showError }; 