console.log("Chatbot script loaded");

function openNewChat() {
    location.reload();
}

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
            const response = await fetch('/get_languages');
            const languages = await response.json();
            if (Array.isArray(languages)) {
                inputLanguageDropdown.innerHTML = '<option value="en">English</option>';
                languages.forEach(language => {
                    if (language.code !== 'en') {
                        const option = document.createElement('option');
                        option.value = language.code;
                        option.textContent = language.name;
                        inputLanguageDropdown.appendChild(option);
                    }
                });
                inputLanguageDropdown.value = 'en';
            }
        } catch (error) {
            console.error('Error fetching languages:', error);
        }
    }

    function handleKeyDown(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            handleSubmitButton();
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
        const inputLanguage = inputLanguageDropdown.value;

        if (!userText && !accumulatedText) return;

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
            queryInput.value = '';
            accumulatedText = '';
            hideLoadingSpinner();
        }
    }

    async function sendMessageToChatbot(message, inputLanguage) {
        try {
            console.log('Sending message to chatbot:', message);
            const response = await fetch('/get_response', {
                method: 'POST',
                body: JSON.stringify({ query: message, input_language: inputLanguage }),
                headers: { 'Content-Type': 'application/json' },
            });

            if (!response.ok) {
                throw new Error(`Request failed with status ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error in sendMessageToChatbot:', error);
            return { general_response: `Error: ${error.message}` };
        }
    }

    // text to speak -> response (only valid for english)
    function speakText(element) {
        const synth = window.speechSynthesis;

        if (synth.speaking || synth.pending) {
            synth.cancel();
            resetSpeakerIcons();
            return;
        }

        const container = element.closest('.formated-response-container');
        if (!container) return;

        const textToSpeak = Array.from(container.querySelectorAll('p'))
            .map(p => p.innerText.trim())
            .filter(text => text.length > 0)
            .join(" ");

        if (!textToSpeak) return;

        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.lang = document.documentElement.lang || navigator.language || 'en-US';

        resetSpeakerIcons();
        element.style.color = 'red';

        utterance.onend = () => {
            element.style.color = 'gold';
        };

        synth.cancel();
        setTimeout(() => synth.speak(utterance), 100);
    }

    function resetSpeakerIcons() {
        document.querySelectorAll('.speaker-icon').forEach(icon => {
            icon.style.color = 'gold';
        });
    }

    function addSpeakerIcon() {
        const inputLanguage = inputLanguageDropdown.value; // Get selected language
        return inputLanguage === 'en' ? `<i class="fas fa-volume-up speaker-icon" style="color: gold; cursor: pointer; margin-left: 10px;"></i>` : '';
    }

    
    function formatChatbotResponse(response) {
        let formattedResponse = "";

        if (response.general_response) {
            formattedResponse += `
                <div class="formated-response-container">
                    <p>${response.general_response.replace(/\n/g, '<br>')}</p>
                    ${addSpeakerIcon()}
                </div>
            `;
        } else {
            formattedResponse += `
                <div class="formated-response-container">
                    <p>Sorry, I can't answer this query :(</p>
                    ${addSpeakerIcon()}
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
                ${addSpeakerIcon()}
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
            messageElement.innerHTML = `<i class="fas fa-user"></i> : ${text}`;
        } else {
            messageElement.id = 'chatbot_area';
            messageElement.innerHTML = `<img src="static/img/feather.png" alt="Feather Icon" width="20" height="20"> : ${text}`;
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
        if (!('webkitSpeechRecognition' in window)) {
            alert('Speech recognition is not supported in this browser.');
            return;
        }
    
        if (isRecording) {
            console.log("Stopping speech recognition...");
            recognition.stop();
            microphoneIcon.style.color = ''; // Reset to default color
            isRecording = false;
    
            if (accumulatedText.trim()) {
                console.log("User stopped mic, sending text:", accumulatedText);
                sendMessage(); // Send text when mic is clicked again
            }
        } else {
            console.log("Starting speech recognition...");
            recognition = new webkitSpeechRecognition();
            recognition.lang = inputLanguageDropdown.value;
            recognition.interimResults = true;
            recognition.continuous = true; // Keep recognizing until user stops it
    
            recognition.onstart = () => {
                console.log("Speech recognition started.");
                microphoneIcon.style.color = 'red';
                isRecording = true;
            };
    
            recognition.onresult = event => {
                console.log("Speech recognition result event triggered.");
                console.log("Raw event results:", event.results);
    
                accumulatedText = Array.from(event.results)
                    .map(res => res[0].transcript)
                    .join(" ");
    
                console.log("Accumulated Text:", accumulatedText);
                queryInput.value = accumulatedText; // Update input field live
            };
    
            recognition.onerror = event => {
                console.error("Speech recognition error:", event.error);
            };
    
            recognition.start();
        }
    }
    
    function handleSubmitButton() {
        console.log("Submit button clicked.");
    
        // Stop speech recognition if it's running
        if (isRecording) {
            console.log("Stopping speech recognition since submit was clicked...");
            recognition.stop();
            microphoneIcon.style.color = ''; // Reset mic button color
            isRecording = false;
        }
    
        // Check if there's text to send
        if (!queryInput.value.trim() && !accumulatedText.trim()) {
            console.log("No text to send.");
            return;
        }
    
        sendMessage();
    }
    

    populateLanguageDropdown();

    document.addEventListener('click', event => {
        if (event.target.classList.contains('speaker-icon')) {
            speakText(event.target);
        }
    });
});
