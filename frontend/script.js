const chatBox = document.getElementById("chat-box");
const input = document.getElementById("message-input");

// 1. Send Message
async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    displayMessage(message, "user");
    input.value = "";

    showLoading();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        removeLoading();
        displayMessage(data.reply, "bot");

    } catch (error) {
        removeLoading();
        displayMessage("Error: Unable to reach server", "bot");
        console.error(error);
    }
}

// 2. Display Message
function displayMessage(message, sender) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);

    msgDiv.textContent = message;
    chatBox.appendChild(msgDiv);

    autoScroll();
}

// 3. Load History
async function loadHistory() {
    try {
        const response = await fetch("/history");
        const data = await response.json();

        data.forEach(msg => {
            displayMessage(msg.text, msg.sender);
        });

    } catch (error) {
        console.error("Error loading history:", error);
    }
}

// 4. Auto Scroll
function autoScroll() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 5. Loading Indicator
function showLoading() {
    const loading = document.createElement("div");
    loading.id = "loading";
    loading.textContent = "Typing...";
    chatBox.appendChild(loading);
    autoScroll();
}

function removeLoading() {
    const loading = document.getElementById("loading");
    if (loading) loading.remove();
}

// Load history when page opens
window.onload = loadHistory;
