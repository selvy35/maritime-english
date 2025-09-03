let exercises = [];
let currentIndex = 0;

// load json data
fetch(`/static/data/unit${unitId}/${section}.json`)
  .then(res => res.json())
  .then(data => {
    exercises = data;
    renderExercise(currentIndex); 
  })
  .catch(err => {
    document.getElementById("exercise-container").innerHTML =
      `<p class="text-danger">⚠️ Failed to load exercises for Unit ${unitId}, Section ${section}</p>`;
    console.error(err);
  });


function renderExercise(index) {
  const ex = exercises[index];
  const container = document.getElementById("exercise-container");
  container.innerHTML = "";

  let html = `<h4 class="mb-3">${ex.prompt}</h4>`;

  if (ex.type === "multiple_choice") {
    html += `<button onclick="playAudio('${ex.audio}')" class="btn btn-primary mb-3">▶️ Play Audio</button>`;
    html += `<div class="d-flex flex-wrap justify-content-center">`;
    ex.choices.forEach(choice => {
      html += `<button class="btn btn-outline-dark m-1 choice-btn" data-choice="${choice}">${choice}</button>`;
    });
    html += `</div>`;
  }

  if (ex.type === "arrange") {
    html += `<button onclick="playAudio('${ex.audio}')" class="btn btn-secondary mb-3">▶️ Play Dialogue</button>`;
    html += `<div id="arrange-area" class="d-flex flex-wrap justify-content-center border p-2 mb-2" style="min-height:50px;"></div>`;
    html += `<div id="word-bank" class="d-flex flex-wrap justify-content-center mt-2">`;
    ex.words.forEach(w => {
      html += `<button 
                class="btn btn-outline-dark m-1 word-btn" 
                data-text="${w.text}" 
                data-meaning="${w.meaning}">
                ${w.text}
              </button>`;
    });
    html += `</div>`;
  }

  if (ex.type === "matching") {
    html += `<div class="row">`;
    html += `<div class="col-md-6">`;
    ex.pairs.forEach((p,i) => {
      html += `<button class="btn btn-outline-primary w-100 m-1 audio-btn" data-audio="${p.audio}">▶️ ${i+1}</button>`;
    });
    html += `</div><div class="col-md-6">`;
    ex.pairs.forEach(p => {
      html += `<button class="btn btn-outline-dark w-100 m-1 text-btn" data-text="${p.text}">${p.text}</button>`;
    });
    html += `</div></div>`;
  }

  container.innerHTML = html;

  // aktifkan pilihan multiple choice
  if (ex.type === "multiple_choice") {
    document.querySelectorAll(".choice-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".choice-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
      });
    });
  }

  // aktifkan arrange
  if (ex.type === "arrange") {
    document.querySelectorAll(".word-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        playAudio(`/speak?text=${btn.dataset.text}`);

        const arrangeArea = document.getElementById("arrange-area");
        const wordBank = document.getElementById("word-bank");

        if (arrangeArea.contains(btn)) {
          // kalau sudah di atas → balikin ke bawah
          wordBank.appendChild(btn);
        } else {
          // kalau masih di bawah → pindahin ke atas
          arrangeArea.appendChild(btn);
        }
      });
    });
  }

  // aktifkan matching
  if (ex.type === "matching") {
    document.querySelectorAll(".audio-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        playAudio(btn.dataset.audio);
        btn.classList.add("active-audio");
      });
    });
    document.querySelectorAll(".text-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const audioBtn = document.querySelector(".audio-btn.active-audio");
        if (!audioBtn) return;

        // simpan pasangan dipilih ke dataset
        if (!ex.selections) ex.selections = [];
        ex.selections.push({
          audio: audioBtn.dataset.audio,
          text: btn.dataset.text
        });

        audioBtn.classList.remove("active-audio");
        audioBtn.disabled = true;
        btn.disabled = true;
      });
    });
  }

  updateProgress();
}

function updateProgress() {
  let percent = ((currentIndex+1) / exercises.length) * 100;
  document.getElementById("progress-bar").style.width = percent + "%";
}

function playAudio(url) {
  new Audio(url).play();
}

// ======================
// Feedback overlay
// ======================
function showFeedback(correct, message) {
  const container = document.getElementById("exercise-container");
  const overlay = document.createElement("div");
  overlay.id = "feedback-screen";
  overlay.className = "p-4 text-center";

  if (correct) {
    overlay.innerHTML = `
      <div class="alert alert-success">
        <h3>✅ Excellent!</h3>
        <p>${message}</p>
        <button class="btn btn-success mt-3" id="continue-btn">Continue</button>
      </div>
    `;
  } else {
    overlay.innerHTML = `
      <div class="alert alert-danger">
        <h3>❌ Oops!</h3>
        <p>${message}</p>
        <button class="btn btn-warning mt-3" id="tryagain-btn">Try Again</button>
      </div>
    `;
  }

  container.innerHTML = "";
  container.appendChild(overlay);

  if (correct) {
    document.getElementById("continue-btn").addEventListener("click", () => {
      currentIndex++;
      if (currentIndex < exercises.length) {
        renderExercise(currentIndex);
      } else {
        container.innerHTML = `
          <h3 class="text-success">🎉 Exercise Complete!</h3>
          <p>Great job, you finished all questions.</p>
        `;
      }
    });
  } else {
    document.getElementById("tryagain-btn").addEventListener("click", () => {
      renderExercise(currentIndex);
    });
  }
}

// ======================
// CHECK button
// ======================
document.getElementById("check-btn").addEventListener("click", () => {
  const ex = exercises[currentIndex];
  let correct = false;

  if (ex.type === "multiple_choice") {
    const selected = document.querySelector(".choice-btn.active");
    if (!selected) {
      alert("Please choose an answer!");
      return;
    }
    correct = selected.dataset.choice === ex.answer;
    showFeedback(correct, correct ? "You chose the right answer!" : `The correct answer was: ${ex.answer}`);
    return;
  }

  if (ex.type === "arrange") {
    const arranged = Array.from(document.querySelectorAll("#arrange-area .word-btn"))
      .map(btn => btn.innerText);
    correct = JSON.stringify(arranged) === JSON.stringify(ex.answer);
    showFeedback(correct, correct ? "Perfect order!" : "Try again, check the order carefully.");
    return;
  }

  if (ex.type === "matching") {
    if (!ex.selections || ex.selections.length < ex.pairs.length) {
      alert("Please complete all matches first!");
      return;
    }
    correct = ex.selections.every(sel => 
      ex.pairs.some(p => p.audio === sel.audio && p.text === sel.text)
    );
    showFeedback(correct, correct ? "All pairs matched correctly!" : "Some matches are wrong, try again.");
    return;
  }
});

// ======================
// SKIP button
// ======================
document.getElementById("skip-btn").addEventListener("click", () => {
  currentIndex++;
  if (currentIndex < exercises.length) {
    renderExercise(currentIndex);
  } else {
    document.getElementById("exercise-container").innerHTML = `
      <h3 class="text-success">🎉 Exercise Complete!</h3>
      <p>Great job, you finished all questions.</p>
    `;
  }
});
