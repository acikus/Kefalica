let operation = '+';
let redCount1 = 0;
let redCount2 = 0;

function updateDisplay() {
  document.getElementById('count1').textContent = redCount1;
  document.getElementById('count2').textContent = redCount2;
  document.getElementById('operation').textContent = operation;
  const result = operation === '+' ? redCount1 + redCount2 : redCount1 - redCount2;
  document.getElementById('result').textContent = result;
}

function toggleCircle(event, row) {
  const circle = event.target;
  const isRed = circle.classList.toggle('red');
  if (row === 1) {
    redCount1 += isRed ? 1 : -1;
  } else {
    redCount2 += isRed ? 1 : -1;
  }
  updateDisplay();
}

function init() {
  const row1 = document.getElementById('row1');
  const row2 = document.getElementById('row2');
  for (let i = 0; i < 5; i++) {
    const c1 = document.createElement('div');
    c1.className = 'circle';
    c1.addEventListener('click', (e) => toggleCircle(e, 1));
    row1.appendChild(c1);

    const c2 = document.createElement('div');
    c2.className = 'circle';
    c2.addEventListener('click', (e) => toggleCircle(e, 2));
    row2.appendChild(c2);
  }

  document.getElementById('operation').addEventListener('click', () => {
    operation = operation === '+' ? '-' : '+';
    updateDisplay();
  });

  updateDisplay();
}

document.addEventListener('DOMContentLoaded', init);
