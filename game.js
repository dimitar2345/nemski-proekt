// Кой иска да бъде милионер? - Web версия

const prizes = [100, 150, 200, 250, 300, 500, 750, 1000, 1500, 2500, 5000, 10000, 20000, 50000, 100000];
let questions = [];
let currentQuestion = 0;
let usedJokers = { fifty: false, pub1: false, pub2: false };
let answerOrder = [];
let disabledAnswers = [];

async function loadQuestions() {
    // Зарежда въпросите от questions.json (ако е на същия сървър)
    try {
        const res = await fetch('questions.json');
        questions = await res.json();
        shuffle(questions);
        questions = questions.slice(0, 15);
        showQuestion();
    } catch (e) {
        document.getElementById('game').innerHTML = '<b style="color:red">Грешка при зареждане на въпросите!</b>';
    }
}

function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
}

function showQuestion() {
    if (currentQuestion >= questions.length) {
        document.getElementById('game').innerHTML = `<h2>Поздравления! Спечели ${prizes[prizes.length-1]} евро! 🎉</h2>`;
        return;
    }
    const q = questions[currentQuestion];
    // Разбъркване на отговорите
    answerOrder = ['А', 'Б', 'В', 'Г'];
    
    disabledAnswers = [];
    // Въпрос
    let html = `<div class='prize-bar'>`;
    for (let i = 0; i < prizes.length; i++) {
        html += `<span class='prize${i===currentQuestion?' active':''}${i<currentQuestion?' done':''}'>${prizes[i]}€</span>`;
    }
    html += `</div>`;
    html += `<div class='question'><b>Въпрос ${currentQuestion+1}:</b> ${q.question}</div>`;
    html += `<div class='answers'>`;
    for (let i = 0; i < 4; i++) {
        const letter = answerOrder[i];
        html += `<button class='answer-btn' id='ans${letter}' onclick='chooseAnswer("${letter}")'>${letter}: ${q.answers[letter]}</button><br>`;
    }
    html += `</div>`;
    html += `<div class='jokers'>
        <button onclick='jokerFifty()' ${usedJokers.fifty?'disabled':''}>50:50</button>
        <button onclick='jokerPub1()' ${usedJokers.pub1?'disabled':''}>Помощ от приятел</button>
        <button onclick='jokerPub2()' ${usedJokers.pub2?'disabled':''}>Помощ публиката</button>
    </div>`;
    html += `<div class='status'>Награда: <b>${prizes[currentQuestion]} евро</b></div>`;
    document.getElementById('game').innerHTML = html;
}

function chooseAnswer(letter) {
    if (disabledAnswers.includes(letter)) return;
    const q = questions[currentQuestion];
    let correctLetter = null;
    for (let l of answerOrder) {
        if (q.answers[l] === q.answers[q.correct_answer]) correctLetter = l;
    }
    for (let l of answerOrder) {
        document.getElementById('ans'+l).classList.remove('correct','wrong');
    }
    if (letter === correctLetter) {
        document.getElementById('ans'+letter).classList.add('correct');
        setTimeout(()=>{
            currentQuestion++;
            showQuestion();
        }, 900);
    } else {
        document.getElementById('ans'+letter).classList.add('wrong');
        document.getElementById('ans'+correctLetter).classList.add('correct');
        setTimeout(()=>{
            document.getElementById('game').innerHTML = `
                <h2>Грешен отговор!<br>Верният беше: ${correctLetter}<br>Твоята награда: ${currentQuestion>0?prizes[currentQuestion-1]:0} евро</h2>
                <button class='retry-btn' onclick='restartGame()'>Опитай пак</button>
            `;
        }, 1200);
    // Рестартира играта (глобална функция)
    
    }
}
function restartGame() {
        currentQuestion = 0;
        usedJokers = { fifty: false, pub1: false, pub2: false };
        disabledAnswers = [];
        loadQuestions();
    }

function jokerFifty() {
    if (usedJokers.fifty) return;
    usedJokers.fifty = true;
    const q = questions[currentQuestion];
    let correctLetter = null;
    let wrongs = [];
    for (let l of answerOrder) {
        if (q.answers[l] === q.answers[q.correct_answer]) correctLetter = l;
        else wrongs.push(l);
    }
    shuffle(wrongs);
    disabledAnswers = wrongs.slice(0,2);
    for (let l of disabledAnswers) {
        document.getElementById('ans'+l).disabled = true;
        document.getElementById('ans'+l).classList.add('disabled');
    }
    showJokerMsg('50:50', 'Два грешни отговора са премахнати!');
}

function jokerPub1() {
    if (usedJokers.pub1) return;
    usedJokers.pub1 = true;
    const q = questions[currentQuestion];
    let correctLetter = null;
    for (let l of answerOrder) {
        if (q.answers[l] === q.answers[q.correct_answer]) correctLetter = l;
    }
    showJokerMsg('Помощ от публика', `Мисля че верния отговор е <b>${correctLetter}</b>`);
}

function jokerPub2() {
    if (usedJokers.pub2) return;
    usedJokers.pub2 = true;
    const q = questions[currentQuestion];
    let correctLetter = null;
    for (let l of answerOrder) {
        if (q.answers[l] === q.answers[q.correct_answer]) correctLetter = l;
    }
    // Генерирай проценти
    let perc = {};
    let rest = 100;
    for (let l of answerOrder) {
        if (l === correctLetter) continue;
        perc[l] = Math.floor(Math.random()*21)+5;
        rest -= perc[l];
    }
    perc[correctLetter] = rest;
    // Сортирай по проценти
    let sorted = [...answerOrder].sort((a,b)=>perc[b]-perc[a]);
    let html = `<b>Диаграма на публиката:</b><div class='audience-chart'>`;
    for (let l of sorted) {
        let barColor = l === correctLetter ? '#4caf50' : '#2196f3';
        html += `
        <div class='audience-row'>
            <span class='audience-label'>${l}:</span>
            <div class='audience-bar-bg'>
                <div class='audience-bar' style='width:${perc[l]}%;background:${barColor}'></div>
            </div>
            <span class='audience-percent'>${perc[l]}%</span>
        </div>`;
    }
    html += `</div>`;
    showJokerMsg('Диаграма на публиката', html);
}

function showJokerMsg(title, msg) {
    const d = document.createElement('div');
    d.className = 'joker-modal';
    d.innerHTML = `<div class='joker-modal-content'><h3>${title}</h3><div>${msg}</div><button onclick='this.parentNode.parentNode.remove()'>OK</button></div>`;
    document.body.appendChild(d);
}

document.addEventListener('DOMContentLoaded', loadQuestions);
