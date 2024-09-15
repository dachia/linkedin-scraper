document.getElementById('scrape-commenters').addEventListener('click', () => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, {action: "scrapeCommenters"});
  });
});

// Add event listener for auto-connect button
document.getElementById('auto-connect').addEventListener('click', () => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, {action: "autoConnect"});
  });
});
