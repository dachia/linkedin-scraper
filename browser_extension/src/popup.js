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

// Add event listener for configure filters button
document.getElementById('configure-filters').addEventListener('click', () => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, {action: "configureFilters"});
  });
});

// Add event listener for scrape search results button
document.getElementById('scrape-search-results').addEventListener('click', () => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, {action: "scrapeSearchResults"});
  });
});
