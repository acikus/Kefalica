const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const overlay = document.getElementById('overlay');

const SCREEN_WIDTH = canvas.width;
const SCREEN_HEIGHT = canvas.height;
const PLAYER_SPEED = 5;

let player = { x: SCREEN_WIDTH / 2 - 20, y: SCREEN_HEIGHT - 60, w: 40, h: 40, speed: PLAYER_SPEED, health: 3 };
let bullets = [];
let enemies = [];
let score = 0;
let wave = 1;
let waveSpawned = false;
let gameState = 'running';

const keys = {};
document.addEventListener('keydown', (e) => {
  keys[e.code] = true;
  if (gameState === 'running') {
    if (e.code === 'KeyS') shoot('increase', 1);
    if (e.code === 'KeyD') shoot('decrease', 1);
    if (e.code === 'KeyA') shoot('increase', 5);
    if (e.code === 'KeyF') shoot('decrease', 5);
  } else if (gameState === 'over') {
    if (e.code === 'KeyR') resetGame();
  }
});
document.addEventListener('keyup', (e) => { keys[e.code] = false; });

function shoot(type, amount) {
  bullets.push({ x: player.x + player.w / 2 - 2, y: player.y, w: 4, h: 8, speed: -7, type, amount });
}

function rand(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function randomColor() { return `rgb(${rand(50,255)},${rand(50,255)},${rand(50,255)})`; }

function getEnemiesForWave(n) {
  if (n === 1) return 2;
  if (n === 2) return 4;
  return n;
}

function spawnWave(n) {
  const count = getEnemiesForWave(n);
  for (let i = 0; i < count; i++) {
    const x = Math.random() * (SCREEN_WIDTH - 120);
    const y = -(i + 1) * 60;
    let shieldX = rand(1, 10);
    let shieldY = rand(1, 10);
    let cockpit = rand(2, 20);
    while (cockpit === shieldX + shieldY) cockpit = rand(2, 20);
    enemies.push({
      x, y, w: 120, h: 40, speed: 1,
      shieldX, shieldY, cockpit,
      colorLeft: randomColor(),
      colorRight: randomColor()
    });
  }
}

function handleHit(e, b) {
  const leftBoundary = e.x + e.w / 3;
  const rightBoundary = e.x + 2 * e.w / 3;
  if (b.x < leftBoundary) {
    e.shieldX += b.type === 'decrease' ? -b.amount : b.amount;
  } else if (b.x < rightBoundary) {
    e.cockpit += b.type === 'decrease' ? -b.amount : b.amount;
  } else {
    e.shieldY += b.type === 'decrease' ? -b.amount : b.amount;
  }
  if (e.shieldX + e.shieldY === e.cockpit) {
    score += 10;
    enemies.splice(enemies.indexOf(e), 1);
  }
}

function resetGame() {
  score = 0; wave = 1; waveSpawned = false; gameState = 'running';
  player.x = SCREEN_WIDTH / 2 - 20; player.y = SCREEN_HEIGHT - 60; player.health = 3;
  bullets = []; enemies = [];
  overlay.style.visibility = 'hidden';
}

function update() {
  if (gameState === 'running') {
    if (enemies.length === 0 && !waveSpawned) {
      spawnWave(wave);
      waveSpawned = true;
    }
    if (keys['ArrowLeft'] && player.x > 0) player.x -= player.speed;
    if (keys['ArrowRight'] && player.x + player.w < SCREEN_WIDTH) player.x += player.speed;
    if (keys['ArrowUp'] && player.y > 0) player.y -= player.speed;
    if (keys['ArrowDown'] && player.y + player.h < SCREEN_HEIGHT) player.y += player.speed;

    bullets.forEach((b) => b.y += b.speed);
    bullets = bullets.filter((b) => b.y + b.h > 0);

    enemies.forEach((e) => e.y += e.speed);
    enemies = enemies.filter((e) => e.y < SCREEN_HEIGHT);

    // Bullet vs enemy collisions
    bullets.forEach((b) => {
      enemies.forEach((e) => {
        if (b.x < e.x + e.w && b.x + b.w > e.x && b.y < e.y + e.h && b.y + b.h > e.y) {
          handleHit(e, b);
          b.remove = true;
        }
      });
    });
    bullets = bullets.filter((b) => !b.remove);

    // Player vs enemy collisions
    enemies.forEach((e) => {
      if (player.x < e.x + e.w && player.x + player.w > e.x && player.y < e.y + e.h && player.y + player.h > e.y) {
        player.health -= 1;
        enemies.splice(enemies.indexOf(e), 1);
        if (player.health <= 0) {
          gameState = 'over';
          overlay.style.visibility = 'visible';
          overlay.textContent = 'КРАЈ – притисни R за рестарт';
        }
      }
    });

    if (enemies.length === 0 && gameState === 'running') {
      wave += 1;
      waveSpawned = false;
    }
  }

  draw();
  requestAnimationFrame(update);
}

function draw() {
  ctx.clearRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);
  // Player
  ctx.fillStyle = '#fff';
  ctx.fillRect(player.x, player.y, player.w, player.h);

  // Bullets
  bullets.forEach((b) => {
    ctx.fillStyle = b.type === 'decrease' ? '#008747' : '#ffa500';
    ctx.fillRect(b.x, b.y, b.w, b.h);
  });

  // Enemies
  enemies.forEach((e) => {
    ctx.fillStyle = e.colorLeft;
    ctx.fillRect(e.x, e.y, e.w / 3, e.h);
    ctx.fillStyle = 'red';
    ctx.fillRect(e.x + e.w / 3, e.y, e.w / 3, e.h);
    ctx.fillStyle = e.colorRight;
    ctx.fillRect(e.x + 2 * e.w / 3, e.y, e.w / 3, e.h);
    ctx.strokeStyle = '#000';
    ctx.strokeRect(e.x, e.y, e.w / 3, e.h);
    ctx.strokeRect(e.x + e.w / 3, e.y, e.w / 3, e.h);
    ctx.strokeRect(e.x + 2 * e.w / 3, e.y, e.w / 3, e.h);
    ctx.fillStyle = '#000';
    ctx.font = '20px sans-serif';
    ctx.fillText(e.shieldX, e.x + 15, e.y + 25);
    ctx.fillText(e.cockpit, e.x + e.w / 2 - 10, e.y + 25);
    ctx.fillText(e.shieldY, e.x + e.w - 35, e.y + 25);
  });

  // UI
  ctx.fillStyle = '#fff';
  ctx.font = '20px sans-serif';
  ctx.fillText(`Резултат: ${score}`, 10, 30);
  ctx.fillText(`Животи: ${player.health}`, 10, 60);
}

update();
