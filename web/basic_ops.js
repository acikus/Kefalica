let num1, num2, correctAnswer;
let operation = '+';
let score = 0;
let attempts = 0;

function updateScore() {
  document.getElementById('score').textContent = `Score: ${score}`;
  document.getElementById('attempts').textContent = `Attempts: ${attempts}`;
}

function generateProblem() {
  document.getElementById('feedback').textContent = '';
  document.getElementById('nextBtn').disabled = true;
  if (operation === '+') {
    do {
      num1 = Math.floor(Math.random() * 5) + 1; // 1-5
      num2 = Math.floor(Math.random() * 5) + 1; // 1-5
    } while (num1 + num2 === 10);
    correctAnswer = num1 + num2;
  } else {
    num1 = Math.floor(Math.random() * 8) + 2; // 2-9
    num2 = Math.floor(Math.random() * (num1 - 1)) + 1; // 1..num1-1
    correctAnswer = num1 - num2;
  }
  document.getElementById('problem').textContent = `${num1} ${operation} ${num2} = ?`;
}

function checkAnswer(val) {
  attempts++;
  updateScore();
  if (val === correctAnswer) {
    score++;
    document.getElementById('feedback').textContent = 'Correct!';
    document.getElementById('nextBtn').disabled = false;
    updateScore();
  } else {
    document.getElementById('feedback').textContent = 'Try again!';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const answersDiv = document.getElementById('answers');
  for (let i = 1; i <= 9; i++) {
    const btn = document.createElement('button');
    btn.textContent = i;
    btn.addEventListener('click', () => checkAnswer(i));
    answersDiv.appendChild(btn);
  }
  document.getElementById('nextBtn').addEventListener('click', generateProblem);
  document.getElementById('toggleOp').addEventListener('click', () => {
    operation = operation === '+' ? '-' : '+';
    document.getElementById('toggleOp').textContent = `Choose operation: ${operation}`;
    generateProblem();
  });
  document.getElementById('restartBtn').addEventListener('click', () => {
    score = 0;
    attempts = 0;
    updateScore();
    generateProblem();
  });
  document.getElementById('endBtn').addEventListener('click', () => {
    document.body.innerHTML = '<p>Thanks for playing!</p>';
  });
  generateProblem();
});
