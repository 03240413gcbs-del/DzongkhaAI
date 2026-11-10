
// ==========================================
// DZONGKHAAI - PROFESSIONAL FRONTEND
// ==========================================


// ==========================================
// 1. DOM ELEMENTS
// ==========================================

const englishInput = document.getElementById("englishText");
const translateButton = document.getElementById("translateBtn");
const copyButton = document.getElementById("copyBtn");

const status = document.getElementById("status");
const output = document.getElementById("translationOutput");
const warning = document.getElementById("warning");

const characterCounter = document.querySelector(".input-limit");


// ==========================================
// 2. APPLICATION STATE
// ==========================================

let isGenerating = false;
let hasResponse = false;

const originalButtonHTML = `
    <span class="button-content">
        <span class="button-icon">✦</span>
        Generate Dzongkha Response
    </span>
    <span class="button-arrow">→</span>
`;

const originalCopyHTML = `<span>▢</span> Copy Response`;


// ==========================================
// 3. GENERATE DZONGKHA RESPONSE
// ==========================================

async function sendMessage() {

    const text = englishInput.value.trim();

    if (isGenerating) return;

    // Validate input
    if (!text) {

        status.textContent = "Please enter a message.";
        status.className = "status-message error";

        englishInput.focus();

        return;
    }

    if (text.length > 3000) {

        status.textContent =
            "Your message exceeds 3000 characters.";

        status.className = "status-message error";

        return;
    }

    // Update application state
    isGenerating = true;
    hasResponse = false;

    translateButton.disabled = true;
    copyButton.disabled = true;

    // Reset copy button
    copyButton.innerHTML = originalCopyHTML;

    // Loading button
    translateButton.innerHTML = `
        <span class="button-content">
            <span class="spinner"></span>
            Generating Dzongkha response...
        </span>
    `;

    // Update status
    status.textContent =
        "DzongkhaAI is processing your message...";

    status.className = "status-message loading";

    output.textContent =
        "Please wait while your Dzongkha response is being generated.";

    warning.textContent = "";

    try {

        // Send request to Flask backend
        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                text: text
            })

        });

        // Parse response
        let data;

        try {

            data = await response.json();

        } catch {

            throw new Error(
                "The server returned an invalid response."
            );

        }

        // Check server response
        if (!response.ok) {

            throw new Error(
                data.error || "Unable to generate a response."
            );

        }

        // Validate AI output
        if (
            typeof data.response !== "string" ||
            !data.response.trim()
        ) {

            throw new Error(
                "The AI returned an empty response."
            );

        }

        // Display Dzongkha response
        output.textContent = data.response;

        warning.textContent = data.warning || "";

        // Success message
        status.textContent =
            "Your Dzongkha response is ready.";

        status.className = "status-message success";

        hasResponse = true;

        copyButton.disabled = false;

    }

    catch (error) {

        console.error(
            "DzongkhaAI generation error:",
            error
        );

        output.textContent =
            "Your response could not be generated. Please try again.";

        warning.textContent = "";

        status.textContent =
            error.message || "Something went wrong.";

        status.className = "status-message error";

        hasResponse = false;

        copyButton.disabled = true;

    }

    finally {

        // Restore application state
        isGenerating = false;

        translateButton.disabled = false;

        translateButton.innerHTML =
            originalButtonHTML;

    }

}


// ==========================================
// 4. COPY DZONGKHA RESPONSE
// ==========================================

async function copyResponse() {

    if (!hasResponse || isGenerating) return;

    const text = output.textContent.trim();

    if (!text) return;

    try {

        await navigator.clipboard.writeText(text);

        status.textContent =
            "Response copied successfully!";

        status.className =
            "status-message success";

        copyButton.innerHTML = "✓ Copied!";

        setTimeout(() => {

            copyButton.innerHTML =
                originalCopyHTML;

        }, 2000);

    }

    catch (error) {

        console.error("Copy error:", error);

        status.textContent =
            "Unable to copy. Please select the text manually.";

        status.className =
            "status-message error";

    }

}


// ==========================================
// 5. CLEAR INPUT
// ==========================================

function clearInput() {

    if (isGenerating) return;

    englishInput.value = "";

    updateCharacterCounter();

    englishInput.focus();

    status.textContent = "";
    status.className = "status-message";

}


// ==========================================
// 6. EXAMPLE PROMPTS
// ==========================================

function usePrompt(prompt) {

    if (isGenerating) return;

    englishInput.value = prompt;

    updateCharacterCounter();

    englishInput.focus();

    status.textContent = "";
    status.className = "status-message";

}


// ==========================================
// 7. ENTER TO GENERATE
// ==========================================

englishInput.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


// ==========================================
// 8. CHARACTER COUNTER
// ==========================================

function updateCharacterCounter() {

    const currentLength =
        englishInput.value.length;

    if (characterCounter) {

        characterCounter.textContent =
            `${currentLength}/3000 characters`;

    }

}

englishInput.addEventListener(
    "input",
    updateCharacterCounter
);


// ==========================================
// 9. INITIAL APPLICATION STATE
// ==========================================

function initializeApp() {

    updateCharacterCounter();

    copyButton.disabled = true;

    copyButton.innerHTML =
        originalCopyHTML;

    translateButton.innerHTML =
        originalButtonHTML;

}

initializeApp();
