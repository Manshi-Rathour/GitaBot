function openNewChat() {
    location.reload(); 
}

console.log("Chatbot script loaded");

// Chatbot
document.addEventListener('DOMContentLoaded', () => {
    const result = document.getElementById('result');
    const queryInput = document.getElementById('queryInput');
    const submitButton = document.getElementById('submitButton');

    if (queryInput && submitButton) {
        queryInput.addEventListener('keydown', handleKeyDown);
        submitButton.addEventListener('click', handleEnterKey);
    }

    function handleKeyDown(event) {
        if (event.key === 'Enter') {
            event.preventDefault(); 
            handleEnterKey();
        }
    }

    function handleEnterKey() {
        if (typeof sendMessage === 'function') {
            sendMessage();
        } else {
            console.error('sendMessage function is not defined.');
        }
    }

    async function sendMessage() {
        console.log("sendMessage function called");
        const userText = queryInput.value.trim();
        if (!userText) return; // Do nothing if the input is empty

        appendMessage('User', userText);
        showLoadingSpinner();

        try {
            const response = await sendMessageToChatbot(userText);
            console.log('Chatbot response:', response);

            // Format and display the chatbot response
            appendMessage('Chatbot', formatChatbotResponse(response));
        } catch (error) {
            console.error('Error in sendMessageToChatbot:', error);
            appendMessage('Error', `Error: ${error.message}`);
        } finally {
            queryInput.value = ''; // Clear input field after sending
            hideLoadingSpinner();
        }
    }

    function formatChatbotResponse(response) {
        let formattedResponse = "";

        // General response
        if (response.general_response) {
            formattedResponse += `
                <div class="formated-response-container">
                    <p>${response.general_response.replace(/\n/g, '<br>')}</p>
                </div>
            `;
        } else {
            formattedResponse += `
                <div class="formated-response-container">
                    <p>Sorry, I can't answer this query :( </p>
                </div>
            `;
        }

        // Detailed response with Bhagavad Gita information
        if (response.id && response.shloka) {
            const [chapter, shlokaNum] = response.id.split('.');
            const formattedChapter = chapter.replace('BG', ''); // Remove 'BG' from chapter string

            formattedResponse += `
            <div class="formated-response-container">
                <p>Chapter: ${formattedChapter}</p>
                <p>Shloka: ${shlokaNum}</p>
                <p>Shloka: ${response.shloka}</p>
                <p>Hindi Meaning: ${response.hin_meaning || 'N/A'}</p>
                <p>English Meaning: ${response.eng_meaning || 'N/A'}</p>
            </div>
        `;
        }

        return formattedResponse.trim();
    }

    function appendMessage(role, text) {
        const messageElement = document.createElement('div');
        messageElement.style.padding = '5px';

        if (role === "User") {
            messageElement.id = 'user_area';
            const icon = '<i class="fas fa-user"></i>';
            messageElement.innerHTML = `${icon} : ${text}`;
        } else {
            messageElement.id = 'chatbot_area';

            // Create the image element for the feather icon
            const icon = document.createElement('img');
            icon.src = 'static/img/feather.png';
            icon.alt = 'Feather Icon';
            icon.style.width = '20px'; 
            icon.style.height = '20px';
            icon.style.verticalAlign = 'middle';

            // Add the icon and text to the messageElement
            messageElement.appendChild(icon);
            messageElement.innerHTML += ` : ${text}`; 
            messageElement.classList.add('bg-dark');
        }

        result.appendChild(messageElement);
        result.scrollTop = result.scrollHeight; // Auto-scroll to the bottom
    }

    async function sendMessageToChatbot(message) {
        try {
            console.log('Sending message to chatbot:', message);

            const response = await fetch('/gitabot', {
                method: 'POST',
                body: JSON.stringify({ message }),
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`Request failed with status ${response.status}`);
            }

            const data = await response.json();
            console.log('Chatbot data:', data);
            return data;
        } catch (error) {
            console.error('Error in sendMessageToChatbot:', error);
            return { general_response: `Error: ${error.message}` };
        }
    }

    let loadingSpinner = null;

    function showLoadingSpinner() {
        loadingSpinner = document.createElement('div');
        loadingSpinner.innerHTML = `
            <div class="spinner-border text-light spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        loadingSpinner.style.marginTop = '10px';
        result.appendChild(loadingSpinner);
    }

    function hideLoadingSpinner() {
        if (loadingSpinner) {
            loadingSpinner.remove();
        }
    }
});
