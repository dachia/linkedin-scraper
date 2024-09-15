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
  if (request.action === "scrapeCommenters" || request.action === "autoConnect") {
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

        sendPostRequest(endpoint, data, userAgent)
          .then(response => {
            if (request.action === "scrapeCommenters") {
              return response.blob();
            } else {
              return response.json();
            }
          })
          .then(result => {
            if (request.action === "scrapeCommenters") {
              const url = window.URL.createObjectURL(result);
              const a = document.createElement('a');
              a.style.display = 'none';
              a.href = url;
              a.download = 'linkedin_profiles.csv';
              document.body.appendChild(a);
              a.click();
              window.URL.revokeObjectURL(url);
            } else {
              console.log('Auto-connect response:', result);
            }
          })
          .catch(error => console.error(`Error during ${request.action}:`, error));
      } else {
        console.error('LinkedIn li_at cookie not found');
      }
    });
  }
});
