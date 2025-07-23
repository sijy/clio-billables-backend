let typingStart = null;
let activeTime = 0;
let timer = null;

const startTimer = () => {
  if (!timer) {
    typingStart = Date.now();
    timer = setInterval(() => activeTime++, 1000);
  }
};

const stopTimer = () => {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
};

document.addEventListener('keydown', (e) => {
  if (document.activeElement && document.activeElement.closest('[aria-label="Message Body"]')) {
    startTimer();
  }
});

document.addEventListener('click', () => {
  if (!document.activeElement.closest('[aria-label="Message Body"]')) {
    stopTimer();
  }
});

const observer = new MutationObserver(() => {
  const sendBtn = document.querySelector('[aria-label*="Send"]');
  if (sendBtn && !sendBtn.dataset.logged) {
    sendBtn.dataset.logged = "true";
    sendBtn.addEventListener('click', async () => {
      stopTimer();
      const body = document.querySelector('[aria-label="Message Body"]')?.innerText || "";
      const seconds = activeTime;
      const emailData = { body, seconds };

      chrome.runtime.sendMessage({ action: 'emailSent', emailData });
      activeTime = 0;
    });
  }
});
observer.observe(document.body, { childList: true, subtree: true });
