const chatBox = document.getElementById("chat-box");
const input = document.getElementById("message-input");
const memories = [];

// 1. Send Message
async function sendMessage() {
    const message = input.value.trim();
    if (!message) return;

    displayMessage(message, "user");
    input.value = "";
    showLoading();

    try {
        const response = await fetch("http://localhost:5000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        removeLoading();

        if (data.reply) {
            typeMessage(data.reply, "bot");

            if (data.memory && !memories.includes(data.memory)) {
                memories.push(data.memory);
                renderMemoryPanel();
            }
        }

    } catch (error) {
        removeLoading();
        displayMessage("Error: Unable to reach server", "bot");
        console.error(error);
    }
}

// 2. Display Message instantly
function displayMessage(message, sender) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);
    msgDiv.textContent = message;
    chatBox.appendChild(msgDiv);
    autoScroll();
}

// 3. Typing animation for bot
function typeMessage(message, sender) {
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);
    chatBox.appendChild(msgDiv);
    autoScroll();

    let i = 0;
    const interval = setInterval(() => {
        msgDiv.textContent += message[i];
        i++;
        autoScroll();
        if (i >= message.length) clearInterval(interval);
    }, 18);
}

// 4. Render memory panel
function renderMemoryPanel() {
    const memList = document.getElementById("memory-list");
    memList.innerHTML = "";

    if (memories.length === 0) {
        memList.innerHTML = '<p class="memory-empty">No memories yet. Start chatting!</p>';
        return;
    }

    memories.forEach((mem, i) => {
        const item = document.createElement("div");
        item.classList.add("memory-item");
        item.innerHTML = `
            <span class="mem-index">#${i + 1}</span>
            <span class="mem-text">${mem}</span>
        `;
        memList.appendChild(item);
    });

    const badge = document.getElementById("memory-count");
    if (badge) {
        badge.textContent = memories.length + " learned";
        badge.classList.remove("pulse");
        void badge.offsetWidth;
        badge.classList.add("pulse");
    }
}

// 5. Load history
async function loadHistory() {
    try {
        const response = await fetch("http://localhost:5000/history");
        const data = await response.json();
        data.forEach(msg => displayMessage(msg.text, msg.sender));
    } catch (error) {
        console.error("Error loading history:", error);
    }
}

// 6. Auto scroll
function autoScroll() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

// 7. Loading indicator
function showLoading() {
    const loading = document.createElement("div");
    loading.id = "loading";
    loading.classList.add("message", "agent");
    loading.innerHTML = '<span class="dot-typing"></span><span class="dot-typing"></span><span class="dot-typing"></span>';
    chatBox.appendChild(loading);
    autoScroll();
}

function removeLoading() {
    const loading = document.getElementById("loading");
    if (loading) loading.remove();
}

// 8. Sidebar topic click
document.querySelectorAll('.sidebar li').forEach(item => {
    item.addEventListener('click', () => {
        input.value = item.textContent.trim();
        sendMessage();
    });
});

// 9. On load — fetch history then personalised welcome
window.onload = async function() {
    await loadHistory();

    try {
        const res = await fetch("http://localhost:5000/welcome");
        const data = await res.json();
        if (data.message) {
            chatBox.innerHTML = "";
            const welcome = document.createElement("div");
            welcome.classList.add("message", "agent");
            welcome.textContent = data.message;
            chatBox.appendChild(welcome);
        }
    } catch(e) {
        console.error("Welcome error:", e);
    }
};