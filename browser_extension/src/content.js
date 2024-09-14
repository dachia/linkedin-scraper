chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "downloadProfiles") {
    chrome.runtime.sendMessage({action: "getLiAtCookie"}, (response) => {
      if (response.li_at) {
        const url = encodeURIComponent(window.location.href);
        const li_at = encodeURIComponent(response.li_at);
        const downloadUrl = `http://localhost:8000/get_csv?url=${url}&li_at=${li_at}`;
        
        fetch(downloadUrl)
          .then(response => response.blob())
          .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'linkedin_profiles.csv';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
          })
          .catch(error => console.error('Error downloading CSV:', error));
      } else {
        console.error('LinkedIn li_at cookie not found');
      }
    });
  }
});
