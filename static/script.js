const chatArea = document.getElementById("chatArea");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const typingIndicator = document.getElementById("typingIndicator");
const voiceBtn = document.getElementById("voiceBtn");
const menuBtn = document.getElementById("menuBtn");
const sidebar = document.querySelector(".sidebar");
const mobileOverlay = document.getElementById("mobileOverlay");

let isSending = false;

function updateViewportHeight() {
  const height = window.visualViewport
    ? window.visualViewport.height
    : window.innerHeight;

  document.documentElement.style.setProperty("--app-height", `${height}px`);
}

updateViewportHeight();
window.addEventListener("resize", updateViewportHeight);

if (window.visualViewport) {
  window.visualViewport.addEventListener("resize", updateViewportHeight);
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatMessage(text) {
  return escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
}

function scrollChatToBottom() {
  requestAnimationFrame(() => {
    chatArea.scrollTo({
      top: chatArea.scrollHeight,
      behavior: "smooth"
    });
  });
}

function addMessage(text, type) {
  const row = document.createElement("div");
  row.className = `message ${type}`;

  if (type === "bot") {
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "KD";
    row.appendChild(avatar);
  }

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = formatMessage(String(text || ""));
  row.appendChild(bubble);

  chatArea.appendChild(row);
  scrollChatToBottom();
}

function setLoading(loading) {
  isSending = loading;
  sendBtn.disabled = loading;
  typingIndicator.classList.toggle("hidden", !loading);

  if (loading) {
    scrollChatToBottom();
  }
}

async function sendMessage(prefilledText = null) {
  if (isSending) return;

  const text = (prefilledText ?? messageInput.value).trim();
  if (!text) return;

  addMessage(text, "user");
  messageInput.value = "";
  autoResize();
  setLoading(true);

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: text
      })
    });

    let data;

    try {
      data = await response.json();
    } catch {
      data = {};
    }

    if (!response.ok) {
      throw new Error(data.error || "Server error");
    }

    addMessage(
      data.reply || "Mujhe response nahi mila.",
      "bot"
    );
  } catch (error) {
    console.error(error);

    addMessage(
      "Connection mein masla aa gaya. Backend check karo aur dobara try karo.",
      "bot"
    );
  } finally {
    setLoading(false);
    messageInput.focus();
    scrollChatToBottom();
  }
}

function autoResize() {
  messageInput.style.height = "auto";
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 120)}px`;
}

sendBtn.addEventListener("click", () => sendMessage());
messageInput.addEventListener("input", autoResize);

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
  }
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    sendMessage(button.dataset.prompt);

    if (window.innerWidth <= 920) {
      sidebar.classList.remove("open");
      mobileOverlay.classList.remove("show");
    }
  });
});

menuBtn.addEventListener("click", () => {
  sidebar.classList.toggle("open");
  mobileOverlay.classList.toggle("show");
});

mobileOverlay.addEventListener("click", () => {
  sidebar.classList.remove("open");
  mobileOverlay.classList.remove("show");
});

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
  const recognition = new SpeechRecognition();

  recognition.lang = "en-PK";
  recognition.interimResults = false;
  recognition.continuous = false;

  voiceBtn.addEventListener("click", () => {
    try {
      voiceBtn.classList.add("listening");
      voiceBtn.querySelector(".mic-icon").textContent = "🔴";
      recognition.start();
    } catch (error) {
      console.error(error);
      voiceBtn.classList.remove("listening");
      voiceBtn.querySelector(".mic-icon").textContent = "🎙️";
    }
  });

  recognition.addEventListener("result", (event) => {
    messageInput.value = event.results[0][0].transcript;
    autoResize();
  });

  recognition.addEventListener("end", () => {
    voiceBtn.classList.remove("listening");
    voiceBtn.querySelector(".mic-icon").textContent = "🎙️";
    messageInput.focus();
  });

  recognition.addEventListener("error", () => {
    voiceBtn.classList.remove("listening");
    voiceBtn.querySelector(".mic-icon").textContent = "🎙️";
  });
} else {
  voiceBtn.addEventListener("click", () => {
    addMessage(
      "Voice input is browser mein supported nahi hai.",
      "bot"
    );
  });
}

messageInput.focus();

// =========================================================
// V7 — WORKSPACE TABS + FARM PROBLEM SOLVER
// =========================================================

const workspaceTabs = document.querySelectorAll(".workspace-tab");
const appViews = document.querySelectorAll(".app-view");
const solverMenuBtn = document.querySelector(".solver-menu-btn");

function closeMobileSidebar() {
  sidebar.classList.remove("open");
  mobileOverlay.classList.remove("show");
}

function switchView(viewId) {
  appViews.forEach((view) => {
    view.classList.toggle("active-view", view.id === viewId);
  });

  workspaceTabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.view === viewId);
  });

  closeMobileSidebar();

  if (viewId === "chatView") {
    setTimeout(() => messageInput.focus(), 150);
  }
}

workspaceTabs.forEach((tab) => {
  tab.addEventListener("click", () => switchView(tab.dataset.view));
});

if (solverMenuBtn) {
  solverMenuBtn.addEventListener("click", () => {
    sidebar.classList.toggle("open");
    mobileOverlay.classList.toggle("show");
  });
}

const farmSolverForm = document.getElementById("farmSolverForm");
const solveBtn = document.getElementById("solveBtn");
const solverEmpty = document.getElementById("solverEmpty");
const solverLoading = document.getElementById("solverLoading");
const solverResult = document.getElementById("solverResult");

async function solveFarmProblem(event) {
  event.preventDefault();

  const district = document.getElementById("solverDistrict").value.trim();
  const acres = document.getElementById("solverAcres").value.trim();
  const soil = document.getElementById("solverSoil").value;
  const season = document.getElementById("solverSeason").value;
  const water = document.getElementById("solverWater").value;

  if (!district || !acres || !soil || !season || !water) return;

  const prompt = `Mere farm ki problem solve karo. Mere paas ${district} mein ${acres} acre ${soil} zameen hai. Season ${season} hai aur water availability ${water} hai. In conditions ke hisab se sab se suitable fasal recommend karo. Sirf seedha practical decision do: recommended crop, kyun suitable hai, basic water advice aur next step. Agar database/tool mein relevant data available ho to usi ko use karo.`;

  solverEmpty.classList.add("hidden");
  solverResult.classList.add("hidden");
  solverLoading.classList.remove("hidden");
  solveBtn.disabled = true;
  solveBtn.innerHTML = '<span>⏳</span> Analyzing Farm...';

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: prompt })
    });

    let data = {};
    try { data = await response.json(); } catch (_) {}

    if (!response.ok) {
      throw new Error(data.error || "Server error");
    }

    solverLoading.classList.add("hidden");
    solverResult.innerHTML = formatMessage(data.reply || "Mujhe recommendation nahi mili.");
    solverResult.classList.remove("hidden");
  } catch (error) {
    console.error(error);
    solverLoading.classList.add("hidden");
    solverResult.innerHTML = "Connection mein masla aa gaya. Backend run karke dobara try karo.";
    solverResult.classList.remove("hidden");
  } finally {
    solveBtn.disabled = false;
    solveBtn.innerHTML = '<span>✨</span> Solve My Farm Problem <span class="solve-arrow">→</span>';
  }
}

if (farmSolverForm) {
  farmSolverForm.addEventListener("submit", solveFarmProblem);
}

// =========================================================
// V10 — dynamic greeting + New Chat
// =========================================================

function updateTimeGreeting() {
  const greeting = document.getElementById("timeGreeting");
  if (!greeting) return;

  const hour = new Date().getHours();
  if (hour < 12) greeting.textContent = "Good Morning";
  else if (hour < 17) greeting.textContent = "Good Afternoon";
  else greeting.textContent = "Good Evening";
}

updateTimeGreeting();

const newChatBtn = document.getElementById("newChatBtn");

function resetChatScreen() {
  if (!chatArea) return;

  chatArea.querySelectorAll(".message").forEach((message) => message.remove());
  messageInput.value = "";
  autoResize();
  switchView("chatView");
  chatArea.scrollTop = 0;
  setTimeout(() => messageInput.focus(), 100);
}

if (newChatBtn) {
  newChatBtn.addEventListener("click", async (event) => {
    event.preventDefault();
    event.stopPropagation();

    newChatBtn.classList.add("working");

    try {
      // If the small /new-chat Flask route is added, backend memory also resets.
      await fetch("/new-chat", { method: "POST" });
    } catch (_) {
      // Frontend reset still works even before backend route is added.
    }

    resetChatScreen();
    newChatBtn.classList.remove("working");
  });
}

// V12 — keep the welcome panel visible after a New Chat reset.
function restoreWelcomePanel() {
  const welcome = document.querySelector("#chatView .welcome-card");
  if (!welcome) return;
  welcome.style.opacity = "1";
  welcome.style.display = "grid";
}

if (newChatBtn) {
  newChatBtn.addEventListener("click", () => {
    setTimeout(restoreWelcomePanel, 40);
  });
}

restoreWelcomePanel();
