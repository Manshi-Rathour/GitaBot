console.log("Chatbot script loaded");

// Function to reload the page
function openNewChat() {
    location.reload(); 
}


// Initialize Google API for Speech Recognition
let recognition;
let isRecording = false;
let accumulatedText = '';
let needsToSendText = false;

document.addEventListener('DOMContentLoaded', () => {
    const result = document.getElementById('result');
    const queryInput = document.getElementById('queryInput');
    const submitButton = document.getElementById('submitButton');
    const inputLanguageDropdown = document.getElementById('inputLanguageDropdown');
    const microphoneIcon = document.getElementById('microphoneIcon');

    if (queryInput && submitButton) {
        queryInput.addEventListener('keydown', handleKeyDown);
        submitButton.addEventListener('click', handleSubmitButton);
    }

    if (microphoneIcon) {
        microphoneIcon.addEventListener('click', toggleSpeechRecognition);
    }

    async function populateLanguageDropdown() {
        try {
            const response = await fetch('/get_languages'); // Fetch supported languages from the backend
            const languages = await response.json();
            if (Array.isArray(languages)) {
                const populateDropdown = (dropdown) => {
                    dropdown.innerHTML = '<option value="en">English</option>'; // Default option
                    languages.forEach(language => {
                        if (language.code !== 'en') { // Add other languages
                            const option = document.createElement('option');
                            option.value = language.code;
                            option.textContent = language.name;
                            dropdown.appendChild(option);
                        }
                    });
                };
                populateDropdown(inputLanguageDropdown);
                inputLanguageDropdown.value = 'en'; // Set default selected option
            }
        } catch (error) {
            console.error('Error fetching languages:', error);
        }
    }

    function handleKeyDown(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleSubmitButton(); // Handle Enter key event
        }
    }

    function handleSubmitButton() {
        if (typeof sendMessage === 'function') {
            sendMessage();
        } else {
            console.error('sendMessage function is not defined.');
        }
    }

    async function sendMessage() {
        console.log("sendMessage function called");
        const userText = queryInput.value.trim();
        const inputLanguage = inputLanguageDropdown.value; // Get selected input language

        if (!userText && !accumulatedText) return; // Do nothing if the input is empty

        const messageText = userText || accumulatedText;
        appendMessage('User', messageText);
        showLoadingSpinner();

        try {
            const response = await sendMessageToChatbot(messageText, inputLanguage);
            console.log('Chatbot response:', response);
            appendMessage('Chatbot', formatChatbotResponse(response));
        } catch (error) {
            console.error('Error in sendMessageToChatbot:', error);
            appendMessage('Error', `Error: ${error.message}`);
        } finally {
            queryInput.value = ''; // Clear input field after sending
            accumulatedText = ''; // Clear the accumulated text
            hideLoadingSpinner();
        }
    }

    async function sendMessageToChatbot(message, inputLanguage) {
        try {
            console.log('Sending message to chatbot:', message);
            const response = await fetch('/get_response', {
                method: 'POST',
                body: JSON.stringify({ query: message, input_language: inputLanguage }),
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

    function formatChatbotResponse(response) {
        let formattedResponse = "";

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

        if (response.id && response.shloka) {
            const [chapter, shlokaNum] = response.id.split('.');
            const formattedChapter = chapter.replace('BG', '');

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

        if (response.sentiment) {
            formattedResponse += `
            <div class="formated-response-container">
                <p><strong>Sentiment Analysis:</strong></p>
                <p>Compound Score: ${response.sentiment.compound}</p>
                <p>Negative: ${response.sentiment.neg}</p>
                <p>Neutral: ${response.sentiment.neu}</p>
                <p>Positive: ${response.sentiment.pos}</p>
                <p>${response.sentiment.message}</p>
                <p><em>${response.sentiment.short_message}</em></p>
                <p><strong>Learning Message:</strong> ${response.sentiment.learning_message}</p>
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

            const icon = document.createElement('img');
            icon.src = 'static/img/feather.png';
            icon.alt = 'Feather Icon';
            icon.style.width = '20px';
            icon.style.height = '20px';
            icon.style.verticalAlign = 'middle';

            messageElement.appendChild(icon);
            messageElement.innerHTML += ` : ${text}`;
        }

        result.appendChild(messageElement);
        result.scrollTop = result.scrollHeight; 
    }

    function showLoadingSpinner() {
        const loadingSpinner = document.createElement('div');
        loadingSpinner.innerHTML = `
            <div class="spinner-border text-light spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        loadingSpinner.style.marginTop = '10px';
        result.appendChild(loadingSpinner);
    }

    function hideLoadingSpinner() {
        const loadingSpinner = result.querySelector('.spinner-border');
        if (loadingSpinner) {
            loadingSpinner.remove();
        }
    }

    async function toggleSpeechRecognition() {
        const inputLanguage = inputLanguageDropdown.value;

        if (!('webkitSpeechRecognition' in window)) {
            alert('Speech recognition is not supported in this browser.');
            return;
        }

        if (isRecording) {
            // Stop the speech recognition
            recognition.stop();
            microphoneIcon.style.color = ''; // Reset microphone icon color
            isRecording = false;

            // Send the accumulated text to backend only if needed
            if (needsToSendText) {
                sendMessage();
                needsToSendText = false; // Reset flag
            }
        } else {
            // Start the speech recognition
            recognition = new webkitSpeechRecognition();
            recognition.lang = inputLanguage;
            recognition.interimResults = true; // Allow interim results to be received
            recognition.maxAlternatives = 1;

            recognition.onstart = () => {
                console.log('Speech recognition started');
                microphoneIcon.style.color = 'red'; // Change mic color to red when recording
                accumulatedText = ''; // Reset accumulated text when starting a new recording
                isRecording = true;
                needsToSendText = false; // Reset flag
            };

            recognition.onresult = (event) => {
                let finalTranscript = '';
                for (const result of event.results) {
                    if (result.isFinal) {
                        finalTranscript = result[0].transcript;
                    }
                }
                if (finalTranscript) {
                    accumulatedText = finalTranscript;
                    appendMessage('User', accumulatedText);
                    needsToSendText = true; // Set flag to true
                }
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
            };

            recognition.start();
        }
    }

    populateLanguageDropdown();
});
