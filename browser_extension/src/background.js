chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getLiAtCookie") {
    chrome.cookies.get({url: "https://www.linkedin.com", name: "li_at"}, (cookie) => {
      sendResponse({li_at: cookie ? cookie.value : null});
    });
    return true;
  }
});
