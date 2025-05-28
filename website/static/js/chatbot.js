// Utility function to format plan responses
function formatPlanResponse(responseText) {
    const lines = responseText.trim().split("\n");
    let plans = [];
    lines.forEach(line => {
        if (line.includes("Plan")) {
            plans.push(`<h3>${line}</h3>`);
        } else if (line.includes("Fee:")) {
            plans.push(`<p><strong>${line}</strong></p>`);
        } else if (line.includes("Data") || line.includes("Voice") || line.includes("SMS")) {
            plans.push(`<p>${line}</p>`);
        } else if (line.includes("Description")) {
            plans.push(`<p><em>${line}</em></p>`);
        } else {
            // For any other line, you can simply add a paragraph tag
            plans.push(`<p>${line}</p>`);
        }
    });
    return `<div class='plan-container'>${plans.join("")}</div>`;
}

// Listen for the form submission
document.getElementById("chat-form").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent page reload

    const inputField = document.getElementById("chat-input");
    const message = inputField.value.trim();
    if (!message) return;

    const chatMessagesContainer = document.getElementById("chat-messages");

    const userMsgDiv = document.createElement("div");
    userMsgDiv.classList.add("message", "user");
    userMsgDiv.innerHTML = `<div class="message-content">${message}</div>`;
    chatMessagesContainer.appendChild(userMsgDiv);

    // Clear the input field
    inputField.value = "";
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

    try {
        const formData = new FormData();
        formData.append("message", message);

        // Send the message via fetch using form data (no JSON header)
        const response = await fetch("/chat", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        console.log("API Response:", data);

        if (!data.message) {
            formattedMessage = "<p>Sorry, I didn't understand your request.</p>";
            formattedMessage = "<p>I'm sorry you're experiencing slow internet. Please try restarting your device and checking your connections. If the issue persists, you may want to contact our technical support team.</p>";
        } else {
            // If the response contains "Plan", format it specially
            if (data.message.includes("Plan")) {
                formattedMessage = formatPlanResponse(data.message);
            } else {
                formattedMessage = `<p>${data.message.trim()}</p>`;
            }
        }

        // Append the bot's formatted response
        const botMsgDiv = document.createElement("div");
        botMsgDiv.classList.add("message", "bot");
        botMsgDiv.innerHTML = `<div class="message-content">${formattedMessage}</div>`;
        chatMessagesContainer.appendChild(botMsgDiv);

        // Auto-scroll to the bottom
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    } catch (error) {
        console.error("Error sending message:", error);
        const botMsgDiv = document.createElement("div");
        botMsgDiv.classList.add("message", "bot");
        botMsgDiv.innerHTML = `<div class="message-content"><p>Sorry, there was a server error. Please try again later.</p></div>`;
        chatMessagesContainer.appendChild(botMsgDiv);
    }
});
