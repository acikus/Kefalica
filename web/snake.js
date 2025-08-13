const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const size = 20; // cell size
const cells = canvas.width / size;
let snake, dir, food, score, running, timer;

function init() {
  snake = [{x: 10, y: 10}];
  dir = {x: 1, y: 0};
  placeFood();
  score = 0;
  running = true;
  updateScore();
  clearInterval(timer);
  timer = setInterval(step, 120);
}

function placeFood() {
  food = {x: Math.floor(Math.random()*cells), y: Math.floor(Math.random()*cells)};
  // ensure food not on snake
  while (snake.some(s => s.x === food.x && s.y === food.y)) {
    food = {x: Math.floor(Math.random()*cells), y: Math.floor(Math.random()*cells)};
  }
}

function updateScore() {
  document.getElementById('score').textContent = `Score: ${score}`;
}

function step() {
  if (!running) return;
  const head = {x: snake[0].x + dir.x, y: snake[0].y + dir.y};
  // collision with walls
  if (head.x < 0 || head.x >= cells || head.y < 0 || head.y >= cells ||
      snake.some(s => s.x === head.x && s.y === head.y)) {
    running = false;
    document.getElementById('score').textContent += ' - Game Over';
    return;
  }
  snake.unshift(head);
  if (head.x === food.x && head.y === food.y) {
    score++;
    updateScore();
    placeFood();
  } else {
    snake.pop();
  }
  draw();
}

function draw() {
  ctx.fillStyle = '#eee';
  ctx.fillRect(0,0,canvas.width,canvas.height);
  ctx.fillStyle = 'green';
  snake.forEach(seg => ctx.fillRect(seg.x*size, seg.y*size, size-1, size-1));
  ctx.fillStyle = 'red';
  ctx.fillRect(food.x*size, food.y*size, size-1, size-1);
}

document.addEventListener('keydown', e => {
  const key = e.key;
  if (key === 'ArrowUp' && dir.y !== 1) dir = {x:0,y:-1};
  else if (key === 'ArrowDown' && dir.y !== -1) dir = {x:0,y:1};
  else if (key === 'ArrowLeft' && dir.x !== 1) dir = {x:-1,y:0};
  else if (key === 'ArrowRight' && dir.x !== -1) dir = {x:1,y:0};
});

document.getElementById('restart').addEventListener('click', init);

document.getElementById('end').addEventListener('click', () => {
  clearInterval(timer);
  document.body.innerHTML = '<p>Thanks for playing!</p>';
});

init();
