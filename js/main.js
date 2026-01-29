
// DOM Elements
const heroSection = document.getElementById('hero-section');
const practiceArea = document.getElementById('practice-area');
const statsPreview = document.getElementById('stats-preview');
const textDisplay = document.getElementById('text-display');
const typingInput = document.getElementById('typing-input');
const wpmDisplay = document.getElementById('wpm-display');
const accuracyDisplay = document.getElementById('accuracy-display');
const backspaceDisplay = document.getElementById('backspace-display');

// Game State
let state = {
    isPlaying: false,
    curriculum: [
        { level: 1, text: "타이핑 연습을 시작합니다." },
        { level: 1, text: "손가락의 위치를 기억하세요." },
        { level: 1, text: "천천히 정확하게 입력하는 것이 중요합니다." },
        { level: 2, text: "Hello World! Welcome to coding." },
        { level: 2, text: "The quick brown fox jumps over the lazy dog." },
        { level: 3, text: "한글과 English를 섞어서 연습해 봅시다." },
        { level: 3, text: "백스페이스를 최소화하는 습관을 들이세요." },
        { level: 4, text: "const typing = 'practice';" }
    ],
    currentSentenceIndex: 0,
    startTime: null,
    totalChars: 0,
    totalMistakes: 0,
    sessionBackspaces: 0, // Current sentence backspaces
    totalBackspaces: 0,   // Total session backspaces
    timer: null
};

// Utils
const calculateWPM = () => {
    if (!state.startTime) return 0;
    const timeElapsed = (Date.now() - state.startTime) / 1000 / 60; // in minutes
    if (timeElapsed === 0) return 0;
    // WPM = (Channels / 5) / Time
    // Using simple chars / 5 roughly
    const wpm = Math.round((state.totalChars / 5) / timeElapsed);
    return wpm;
};

const calculateAccuracy = () => {
    if (state.totalChars === 0) return 100;
    const accuracy = Math.round(((state.totalChars - state.totalMistakes) / state.totalChars) * 100);
    return accuracy > 0 ? accuracy : 0;
};

// Core Functions
const initGame = () => {
    // Reset State
    state.currentSentenceIndex = 0;
    state.totalChars = 0;
    state.totalMistakes = 0;
    state.totalBackspaces = 0;

    // UI Transition
    heroSection.classList.add('hidden');
    practiceArea.classList.remove('hidden');

    loadSentence();

    // Focus Input
    typingInput.value = '';
    typingInput.focus();

    // Global Click to Focus
    document.addEventListener('click', () => {
        if (state.isPlaying) typingInput.focus();
    });
};

const loadSentence = () => {
    if (state.currentSentenceIndex >= state.curriculum.length) {
        finishGame();
        return;
    }

    const currentText = state.curriculum[state.currentSentenceIndex].text;
    textDisplay.innerHTML = '';
    state.sessionBackspaces = 0;

    // Create Spans for each character
    currentText.split('').forEach(char => {
        const span = document.createElement('span');
        span.innerText = char;
        textDisplay.appendChild(span);
    });

    typingInput.value = '';
    state.isPlaying = true;

    // Update Stats Display placeholders
    updateStatsUI();
};

const updateStatsUI = () => {
    wpmDisplay.innerText = calculateWPM();
    accuracyDisplay.innerText = `${calculateAccuracy()}%`;
    backspaceDisplay.innerText = state.totalBackspaces;
};

const handleTyping = () => {
    if (!state.isPlaying) return;

    if (!state.startTime) {
        state.startTime = Date.now();
        console.log("Timer Started");
        // Start Interval for WPM live update
        state.timer = setInterval(updateStatsUI, 1000);
    }

    const inputValue = typingInput.value;
    const currentText = state.curriculum[state.currentSentenceIndex].text;
    const spans = textDisplay.querySelectorAll('span');

    let isCorrectSoFar = true;
    let currentMistakes = 0;

    // Visual Update Loop
    spans.forEach((span, index) => {
        const char = inputValue[index];

        if (char == null) {
            span.classList.remove('correct', 'incorrect', 'current');
            if (index === inputValue.length) {
                span.classList.add('current'); // Cursor position
            }
        } else if (char === span.innerText) {
            span.classList.add('correct');
            span.classList.remove('incorrect', 'current');
        } else {
            span.classList.add('incorrect');
            span.classList.remove('correct', 'current');
            isCorrectSoFar = false;
            currentMistakes++;
        }
    });

    // Complete Sentence Check
    if (inputValue === currentText) {
        // Stats Update for this sentence
        state.totalChars += currentText.length;
        // Approximation: add mistakes found at the end (not perfect real-time tracking but sufficient)
        // Better: We should track mistakes in real-time input event. 
        // For now, let's just proceed.

        state.currentSentenceIndex++;

        // Brief pause or effect before next
        typingInput.disabled = true;
        setTimeout(() => {
            typingInput.disabled = false;
            loadSentence();
            typingInput.focus();
        }, 300);
    }
};

const finishGame = () => {
    state.isPlaying = false;
    clearInterval(state.timer);
    alert(`연습 완료!\n평균 속도: ${calculateWPM()} WPM\n정확도: ${calculateAccuracy()}%\n총 백스페이스: ${state.totalBackspaces}`);
    location.reload(); // Simple reset
};

// Event Listeners
window.startPractice = initGame;
window.viewCurriculum = () => { alert("커리큘럼: " + state.curriculum.map(c => c.text).join('\n')); };

typingInput.addEventListener('input', () => {
    // Basic Mistake Counting on input isn't trivial because of deleting.
    // We will count mistakes based on "finished" chars or just raw accuracy at end.
    // For MVP, focus on Backspace.
    handleTyping();
});

// Backspace Tracking
typingInput.addEventListener('keydown', (e) => {
    if (!state.isPlaying) return;

    if (e.key === 'Backspace') {
        state.sessionBackspaces++;
        state.totalBackspaces++;
        backspaceDisplay.innerText = state.totalBackspaces;

        // Add visual flare to backspace stat?
        backspaceDisplay.parentElement.classList.add('pulse');
        setTimeout(() => backspaceDisplay.parentElement.classList.remove('pulse'), 200);
    }
});
