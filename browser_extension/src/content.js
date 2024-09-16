function getLiAtCookie(callback) {
  chrome.runtime.sendMessage({action: "getLiAtCookie"}, (response) => {
    callback(response.li_at);
  });
}

function getEncodedUrl() {
  return encodeURIComponent(window.location.href);
}

function getUserAgent() {
  return navigator.userAgent;
}

function fetchAndDownloadCsv(url, filename, userAgent) {
  fetch(url, {
    headers: {
      'User-Agent': userAgent
    }
  })
    .then(response => response.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    })
    .catch(error => console.error('Error downloading CSV:', error));
}

function sendPostRequest(url, data, userAgent) {
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': userAgent
    },
    body: JSON.stringify(data)
  });
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (["scrapeCommenters", "autoConnect", "configureFilters", "scrapeSearchResults"].includes(request.action)) {
    getLiAtCookie((li_at) => {
      if (li_at) {
        const url = window.location.href;
        const userAgent = getUserAgent();
        const endpoint = 'http://localhost:8000/scrape';
        
        const data = {
          action: request.action,
          url: url,
          li_at: li_at,
          user_agent: userAgent
        };

        if (request.action === "configureFilters") {
          // You can add a prompt here to get filter values from the user
          // For now, we'll use some example filters
          data.filters = {
            current_company: "Example Company",
            past_company: "Past Company",
            locations: ["New York", "San Francisco"],
            connections: "2nd",
            current_role: "Software Engineer"
          };
        }

        sendPostRequest(endpoint, data, userAgent)
          .then(response => {
            if (request.action === "scrapeCommenters" || request.action === "scrapeSearchResults") {
              return response.blob();
            }
            return response.json();
          })
          .then(result => {
            if (request.action === "scrapeCommenters" || request.action === "scrapeSearchResults") {
              // Handle CSV download
              const filename = request.action === "scrapeCommenters" ? 'linkedin_profiles.csv' : 'linkedin_profile_links.csv';
              const url = window.URL.createObjectURL(result);
              const a = document.createElement('a');
              a.style.display = 'none';
              a.href = url;
              a.download = filename;
              document.body.appendChild(a);
              a.click();
              window.URL.revokeObjectURL(url);
            } else if (request.action === "configureFilters") {
              // Handle filter configuration result
              if (result.success) {
                alert(`Filters configured successfully. New URL: ${result.filtered_url}`);
                // Optionally, navigate to the new URL
                // window.location.href = result.filtered_url;
              } else {
                alert(`Error configuring filters: ${result.error}`);
              }
            } else {
              console.log(`${request.action} response:`, result);
            }
          })
          .catch(error => console.error(`Error during ${request.action}:`, error));
      } else {
        console.error('LinkedIn li_at cookie not found');
      }
    });
  }
});
