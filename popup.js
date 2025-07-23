const SERVER = "http://localhost:3000"; // your Express server

async function loadMatters(token) {
  const res = await fetch(`${SERVER}/api/clio/matters`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  const data = await res.json();
  const select = document.getElementById("matterSelect");

  data?.matters?.forEach(m => {
    const option = document.createElement("option");
    option.value = m.id;
    option.textContent = m.display_number + ": " + m.description;
    select.appendChild(option);
  });
}

async function generateSummary(content) {
  const res = await fetch(`${SERVER}/api/gemini/summary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content })
  });

  const data = await res.json();
  return data.summary;
}

document.addEventListener('DOMContentLoaded', async () => {
  const token = localStorage.getItem("clio_token"); // assume you stored it here

  const duration = localStorage.getItem("email_draft_duration") || "1";
  document.getElementById("duration").textContent = duration;

  // Grab last email body
  chrome.tabs.executeScript({
    code: `document.querySelector('[role="textbox"]').innerText;`
  }, async (results) => {
    const content = results?.[0] || "";
    const summary = await generateSummary(content);
    document.getElementById("summary").value = summary;
  });

  await loadMatters(token);

  document.getElementById("submit").onclick = async () => {
    const description = document.getElementById("summary").value;
    const matter_id = document.getElementById("matterSelect").value;

    const res = await fetch(`${SERVER}/api/clio/time-entry`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        matter_id,
        description,
        duration: (parseFloat(duration) / 60).toFixed(2)
      })
    });

    const result = await res.json();
    document.getElementById("status").textContent = result.success ? "✅ Logged!" : "❌ Failed!";
  };
});
