console.log("Chatbot script loaded");

function openNewChat() {
    location.reload();
}

let recognition;
let isRecording = false;
let accumulatedText = '';
let needsToSendText = false;

// UI strings shown around the response block, localized per language
const UI_STRINGS = {
    en: {
        chapter: 'Chapter',
        shloka: 'Shloka',
        meaning: 'Meaning',
        notAnswer: "Sorry, I can't answer this query :("
    },
    hi: {
        chapter: 'अध्याय',
        shloka: 'श्लोक',
        meaning: 'अर्थ',
        notAnswer: 'क्षमा करें, मैं इस प्रश्न का उत्तर नहीं दे सकता :('
    }
};

// Voices load asynchronously in Chrome — cache them once available.
let cachedVoices = [];
let speechWarmedUp = false;

// Chrome can garbage-collect SpeechSynthesisUtterance objects that aren't
// referenced anywhere else, especially for longer text that takes a moment
// to queue — this silently kills speech with no error. Keeping every
// in-flight utterance in this array prevents that.
let activeUtterances = [];
let keepAliveInterval = null;

function loadVoices() {
    cachedVoices = window.speechSynthesis.getVoices();
}
loadVoices();
if ('speechSynthesis' in window && 'onvoiceschanged' in window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = loadVoices;
}

// Chrome silently drops the very first speak() call in a page session.
// Firing one silent, near-instant utterance up front "uses up" that
// dropped call so the user's first real click actually produces sound.
function warmUpSpeechSynthesis() {
    if (speechWarmedUp || !('speechSynthesis' in window)) return;
    speechWarmedUp = true;
    try {
        const warmup = new SpeechSynthesisUtterance(' ');
        warmup.volume = 0;
        warmup.rate = 10;
        window.speechSynthesis.speak(warmup);
    } catch (e) {
        console.warn('Speech warm-up failed (non-critical):', e);
    }
}

if ('speechSynthesis' in window) {
    if (window.speechSynthesis.getVoices().length > 0) {
        warmUpSpeechSynthesis();
    } else {
        window.speechSynthesis.addEventListener('voiceschanged', warmUpSpeechSynthesis, { once: true });
    }
    document.addEventListener('click', warmUpSpeechSynthesis, { once: true });
}

// Pick the best available voice for a given language, preferring a
// natural/Google voice over the default robotic one.
function pickVoice(langCode) {
    const voices = cachedVoices.length ? cachedVoices : window.speechSynthesis.getVoices();
    const wantLang = langCode === 'hi' ? 'hi-IN' : 'en-US';

    let voice = voices.find(v => v.lang === wantLang);
    if (!voice) {
        voice = voices.find(v => v.lang.startsWith(langCode));
    }
    const betterMatch = voices.find(v => v.lang.startsWith(langCode) && /Google/i.test(v.name));
    if (betterMatch) voice = betterMatch;

    return voice || null;
}

// Split long text into sentence-sized pieces. Chrome has known bugs with
// very long single utterances (silent failure, or stopping after ~15s),
// so speaking a queue of shorter utterances is much more reliable.
// Splits on Hindi danda (।), standard sentence enders (. ! ?), and
// newlines, then re-merges tiny fragments up to ~180 chars per chunk.
function splitIntoSpeechChunks(text, maxLen = 180) {
    const rough = text
        .split(/(?<=[।.!?])\s+|\n+/)
        .map(s => s.trim())
        .filter(Boolean);

    const chunks = [];
    let current = '';

    for (const sentence of rough) {
        const candidate = current ? `${current} ${sentence}` : sentence;
        if (candidate.length > maxLen && current) {
            chunks.push(current);
            current = sentence;
        } else {
            current = candidate;
        }
    }
    if (current) chunks.push(current);

    return chunks.length ? chunks : [text];
}

function stopKeepAlive() {
    if (keepAliveInterval) {
        clearInterval(keepAliveInterval);
        keepAliveInterval = null;
    }
}

// Chrome has a bug where long speech queues can just halt partway through.
// Periodically pausing/resuming nudges the engine and keeps it going.
function startKeepAlive() {
    stopKeepAlive();
    keepAliveInterval = setInterval(() => {
        const synth = window.speechSynthesis;
        if (!synth.speaking) {
            stopKeepAlive();
            return;
        }
        synth.pause();
        synth.resume();
    }, 5000);
}

// Render a Markdown string to sanitized HTML. Falls back to a plain
// newline->br conversion if marked/DOMPurify failed to load (e.g. offline).
function renderMarkdown(text) {
    if (typeof marked === 'undefined') {
        return text.replace(/\n/g, '<br>');
    }

    const rawHtml = marked.parse(text);

    if (typeof DOMPurify !== 'undefined') {
        return DOMPurify.sanitize(rawHtml);
    }

    return rawHtml;
}


function typeWriterEffect(container, fullText, { totalSteps = 200, stepDelay = 40 } = {}) {
    const chunkSize = Math.max(1, Math.ceil(fullText.length / totalSteps));
    let currentIndex = 0;

    return new Promise(resolve => {
        const cursor = '<span class="typing-cursor">▍</span>';

        const interval = setInterval(() => {
            currentIndex = Math.min(currentIndex + chunkSize, fullText.length);
            const partialText = fullText.slice(0, currentIndex);
            const isDone = currentIndex >= fullText.length;

            container.innerHTML = renderMarkdown(partialText) + (isDone ? '' : cursor);

            const result = document.getElementById('result');
            if (result) result.scrollTop = result.scrollHeight;

            if (isDone) {
                clearInterval(interval);
                resolve();
            }
        }, stepDelay);
    });
}

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
                inputLanguageDropdown.innerHTML = '';
                languages.forEach(language => {
                    const option = document.createElement('option');
                    option.value = language.code;
                    option.textContent = language.name;
                    inputLanguageDropdown.appendChild(option);
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

        if (typeof sendMessage === 'function') {
            sendMessage();
        } else {
            console.error('sendMessage function is not defined.');
        }
    }

    async function sendMessage() {
        console.log("sendMessage function called");
        const userText = queryInput.value.trim();
        const language = inputLanguageDropdown.value;

        if (!userText && !accumulatedText) return;

        const messageText = userText || accumulatedText;
        appendMessage('User', messageText);
        showLoadingSpinner();

        queryInput.value = '';
        accumulatedText = '';

        try {
            const response = await sendMessageToChatbot(messageText, language);
            console.log('Chatbot response:', response);
            hideLoadingSpinner();
            await appendChatbotResponse(response);
        } catch (error) {
            console.error('Error in sendMessageToChatbot:', error);
            hideLoadingSpinner();
            appendMessage('Error', `Error: ${error.message}`);
        }
    }

    async function sendMessageToChatbot(message, language) {
        try {
            console.log('Sending message to chatbot:', message, 'language:', language);
            const response = await fetch('/get_response', {
                method: 'POST',
                body: JSON.stringify({ query: message, language }),
                headers: { 'Content-Type': 'application/json' },
            });

            if (!response.ok) {
                throw new Error(`Request failed with status ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error in sendMessageToChatbot:', error);
            return { general_response: `Error: ${error.message}`, language: 'en' };
        }
    }

    // Speak the visible text of a response block, in the correct language,
    // with the best available voice, chunked for reliability on long text.
    function speakText(element) {
        const synth = window.speechSynthesis;

        if (!synth) {
            alert('Text-to-speech is not supported in this browser.');
            return;
        }

        // If something is already playing, treat this click as "stop".
        if (synth.speaking || synth.pending) {
            synth.cancel();
            activeUtterances = [];
            stopKeepAlive();
            resetSpeakerIcons();
            return;
        }

        const container = element.closest('.formated-response-container');
        if (!container) return;

        const textToSpeak = Array.from(container.querySelectorAll('p, li, h1, h2, h3, h4, h5, h6, td, th'))
            .map(el => el.innerText.trim())
            .filter(text => text.length > 0)
            .join(". ");

        if (!textToSpeak) return;

        const langAttr = container.getAttribute('lang')
            || container.closest('[lang]')?.getAttribute('lang')
            || 'en';

        const doSpeak = () => {
            const voice = pickVoice(langAttr);
            const chunks = splitIntoSpeechChunks(textToSpeak);

            activeUtterances = chunks.map(chunk => {
                const utterance = new SpeechSynthesisUtterance(chunk);
                if (voice) {
                    utterance.voice = voice;
                    utterance.lang = voice.lang;
                } else {
                    utterance.lang = langAttr === 'hi' ? 'hi-IN' : 'en-US';
                }
                utterance.rate = langAttr === 'hi' ? 0.9 : 1;
                utterance.pitch = 1;
                return utterance;
            });

            if (!voice && langAttr === 'hi') {
                console.warn('No Hindi voice found on this browser/device — falling back to default voice, which may sound off.');
            }

            resetSpeakerIcons();
            element.style.color = 'red';

            const last = activeUtterances[activeUtterances.length - 1];
            last.onend = () => {
                element.style.color = 'gold';
                activeUtterances = [];
                stopKeepAlive();
            };
            last.onerror = () => {
                element.style.color = 'gold';
                activeUtterances = [];
                stopKeepAlive();
            };

            // Queue every chunk — the browser plays them back-to-back.
            activeUtterances.forEach(u => synth.speak(u));
            startKeepAlive();
        };

        // Make sure the engine is warmed up (covers the case where the
        // user's very first click on the page IS a speaker icon).
        warmUpSpeechSynthesis();

        // If voices haven't loaded yet, wait for them once, then speak.
        if (!cachedVoices.length && synth.getVoices().length === 0) {
            synth.addEventListener('voiceschanged', () => {
                loadVoices();
                doSpeak();
            }, { once: true });
        } else {
            doSpeak();
        }
    }

    function resetSpeakerIcons() {
        document.querySelectorAll('.speaker-icon').forEach(icon => {
            icon.style.color = 'gold';
        });
    }

    function addSpeakerIcon() {
        return `<i class="fas fa-volume-up speaker-icon" style="color: gold; cursor: pointer; margin-left: 10px;"></i>`;
    }

    // Appends the chatbot's reply to #result and animates the general_response
    // in with the typewriter effect. The shloka/meaning block (if any) fades
    // in right after the typing finishes, so it reads like a natural
    // continuation rather than popping in mid-sentence.
    async function appendChatbotResponse(response) {
        const language = response.language === 'hi' ? 'hi' : 'en';
        const strings = UI_STRINGS[language];
        const hiClass = language === 'hi' ? ' lang-hi' : '';

        const messageElement = document.createElement('div');
        messageElement.style.padding = '5px';
        messageElement.id = 'chatbot_area';
        messageElement.setAttribute('lang', language);
        messageElement.innerHTML = `<img src="static/img/feather.png" alt="Feather Icon" width="20" height="20"> : `;

        const body = document.createElement('span');
        messageElement.appendChild(body);
        result.appendChild(messageElement);
        result.scrollTop = result.scrollHeight;

        const generalText = response.general_response;

        const responseContainer = document.createElement('div');
        responseContainer.className = generalText
            ? `formated-response-container markdown-body${hiClass}`
            : `formated-response-container${hiClass}`;
        body.appendChild(responseContainer);

        if (generalText) {
            await typeWriterEffect(responseContainer, generalText);
            responseContainer.insertAdjacentHTML('beforeend', addSpeakerIcon());
        } else {
            responseContainer.innerHTML = `<p>${strings.notAnswer}</p>${addSpeakerIcon()}`;
        }

        if (response.id && response.shloka) {
            const [chapter, shlokaNum] = response.id.split('.');
            const formattedChapter = chapter.replace('BG', '');
            const meaning = response.meaning
                || (language === 'hi' ? response.hin_meaning : response.eng_meaning)
                || 'N/A';

            const shlokaContainer = document.createElement('div');
            shlokaContainer.className = `formated-response-container shloka-fade-in${hiClass}`;
            shlokaContainer.setAttribute('lang', language);
            shlokaContainer.innerHTML = `
                <p><strong>${strings.chapter}:</strong> ${formattedChapter}</p>
                <p><strong>${strings.shloka}:</strong> ${shlokaNum}</p>
                <p class="shloka-text">${response.shloka}</p>
                <p><strong>${strings.meaning}:</strong> ${meaning}</p>
                ${addSpeakerIcon()}
            `;
            body.appendChild(shlokaContainer);
        }

        result.scrollTop = result.scrollHeight;
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
            // hi-IN gives noticeably better recognition for Hindi speech
            // than the bare 'hi' code.
            recognition.lang = inputLanguageDropdown.value === 'hi' ? 'hi-IN' : 'en-US';
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

    populateLanguageDropdown();

    document.addEventListener('click', event => {
        if (event.target.classList.contains('speaker-icon')) {
            speakText(event.target);
        }
    });
});