// =========================
// Game State
// =========================
let currentQuestion = null;
let currentAnswer = '';
let score = 0;
let gameOver = false;
const targetScore = 100;
const answersHistory = [];

// =========================
// Data
// =========================
const maritimeTerms = [
    { term: 'Anchor', letter: 'A' },
    { term: 'Bow', letter: 'B' },
    { term: 'Crew', letter: 'C' },
    { term: 'Deck', letter: 'D' },
    { term: 'One', letter: '1' },
    { term: 'Two', letter: '2' }
];

// =========================
// Helpers
// =========================
async function playTTS(text) {
    try {
        const response = await fetch("/speak", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        if (!response.ok) {
            throw new Error("Failed to generate audio.");
        }

        const data = await response.json();
        new Audio(data.url).play();
    } catch (err) {
        console.error(err);
        alert("Error playing audio.");
    }
}

function recordAnswer(question, correctAnswer, userAnswer, isCorrect) {
    answersHistory.push({
        question,
        correct_answer: correctAnswer,
        user_answer: userAnswer,
        is_correct: isCorrect
    });
}

// =========================
// Game Flow
// =========================
function playRandomTerm() {
    if (gameOver) return;

    const randomIndex = Math.floor(Math.random() * maritimeTerms.length);
    currentQuestion = maritimeTerms[randomIndex];
    currentAnswer = currentQuestion.letter;

    const feedback = document.getElementById('feedback');
    feedback.className = "alert alert-info"; // reset + info
    feedback.innerText = `Playing audio for: "${currentQuestion.term}"`;

    playTTS(currentQuestion.term);
}

function updateScore(points) {
    if (gameOver) return;

    score = Math.min(score + points, targetScore);

    // update UI score
    document.getElementById('score').innerText = score;

    const hiddenScore = document.getElementById('hidden-score');
    if (hiddenScore) hiddenScore.value = score;

    // update progress bar
    const progress = (score / targetScore) * 100;
    const progressBar = document.getElementById("progress-bar");
    progressBar.style.width = `${progress}%`;
    progressBar.setAttribute("aria-valuenow", score);

    if (score >= targetScore) finishGame();
}

function finishGame() {
    gameOver = true;

    // disable tombol
    document.querySelectorAll('.letter-btn, #play-audio')
        .forEach(btn => btn.disabled = true);

    // feedback
    const feedback = document.getElementById('feedback');
    feedback.className = "alert alert-success";
    feedback.innerText = "Warm-Up complete! 🎉 You’re ready to sail 🚢";

    // tampilkan skor final di modal
    document.getElementById("final-score").innerText = score;
    new bootstrap.Modal(document.getElementById('completionModal')).show();

    // simpan history ke server
    fetch("/warmup_history_batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ unit: 1, history: answersHistory })
    })
    .then(res => res.json())
    .then(data => console.log("History saved:", data))
    .catch(err => console.error("Save error:", err));
}

// =========================
// Event Listeners
// =========================
document.getElementById('play-audio').addEventListener('click', playRandomTerm);

document.querySelectorAll('.letter-btn').forEach(button => {
    button.addEventListener('click', function() {
        if (gameOver) return;

        const selected = this.getAttribute('data-value');
        const feedback = document.getElementById('feedback');
        feedback.classList.remove('d-none');

        if (selected === currentAnswer) {
            feedback.className = "alert alert-success";
            feedback.innerText = "Correct!";
            updateScore(10);
            recordAnswer(currentQuestion.term, currentAnswer, selected, true);
        } else {
            feedback.className = "alert alert-danger";
            feedback.innerText = `Wrong! The correct answer was "${currentAnswer}".`;
            recordAnswer(currentQuestion.term, currentAnswer, selected, false);
        }

        if (!gameOver) setTimeout(playRandomTerm, 1000);
    });
});

// =========================
// Start Game
// =========================
playRandomTerm();
