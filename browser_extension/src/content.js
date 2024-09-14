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

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "scrapeCommenters") {
    getLiAtCookie((li_at) => {
      if (li_at) {
        const url = getEncodedUrl();
        const encodedLiAt = encodeURIComponent(li_at);
        const userAgent = encodeURIComponent(getUserAgent());
        const downloadUrl = `http://localhost:8000/scrape-commenters?url=${url}&li_at=${encodedLiAt}&user_agent=${userAgent}`;
        
        fetchAndDownloadCsv(downloadUrl, 'linkedin_profiles.csv', getUserAgent());
      } else {
        console.error('LinkedIn li_at cookie not found');
      }
    });
  }
});
