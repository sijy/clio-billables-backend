chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'emailSent') {
    fetch('https://your-render-backend.onrender.com/api/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(message.emailData)
    }).then(res => res.json())
      .then(data => {
        console.log('Logged to Clio:', data);
      });
  }
});
