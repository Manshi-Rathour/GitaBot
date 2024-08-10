document.getElementById('query-form').addEventListener('submit', function (event) {
    event.preventDefault();

    let query = event.target.query.value;

    if (!query) {
        alert("Please enter a query.");
        return;
    }

    fetch('/get_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        let responseContainer = document.getElementById('response-container');
        responseContainer.innerHTML = '';
        
        if (data.status === 'success') {
            responseContainer.style.display = 'block'; // Show the response container only after generating the response
            
            responseContainer.innerHTML += `
                <div class="response-wrapper">
                    <div class="guidance-column">
                        <h3 class="subtitle underline">Guidance Based on Your Query</h3>
                        <p>${data.general_response}</p>
                        <h3 class="subtitle underline">From Bhagavad Gita</h3>
                        <p>Chapter: ${data.shloka_id.split('.')[0].substring(2)}</p>
                        <p>Shloka: ${data.shloka_id.split('.')[1]}</p>
                        <p>Shloka: ${data.shloka}</p>
                        <p>Hindi Meaning: ${data.hin_meaning}</p>
                        <p>English Meaning: ${data.eng_meaning}</p>
                    </div>
                    <div class="sentiment-column">
                        <h3>Sentiment Evaluation</h3>
                        <h4 class="subtitle underline">Understanding the Emotional Tone</h4>
                        <p>Compound: ${data.sentiment.compound.toFixed(2)}</p>
                        <p>Negative: ${data.sentiment.neg.toFixed(2)}</p>
                        <p>Neutral: ${data.sentiment.neu.toFixed(2)}</p>
                        <p>Positive: ${data.sentiment.pos.toFixed(2)}</p>
                        <p><b>Sentiment Message: </b> ${data.sentiment.message}</p>
                        <p><b>Short Message: </b> ${data.sentiment.short_message}</p>
                        <p><b>Learning Message: </b> ${data.sentiment.learning_message}</p>
                    </div>
                </div>
            `;
        } else {
            responseContainer.innerHTML = `<p class='formated-response-container'>${data.message}</p>`;
        }
    })
    .catch(error => console.error('Error:', error));
});
