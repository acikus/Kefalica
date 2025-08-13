let firstCard = null;
let secondCard = null;
let lockBoard = false;
let matches = 0;

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

function createBoard() {
  const emojis = ['🚗','🚕','🚌','🚓','🚑','🚒','🚜','🚛'];
  const pairEmojis = shuffle(emojis.concat(emojis));
  const board = document.getElementById('board');
  board.innerHTML = '';
  pairEmojis.forEach(emoji => {
    const card = document.createElement('div');
    card.className = 'card';
    card.dataset.emoji = emoji;
    card.textContent = '?';
    card.addEventListener('click', onCardClick);
    board.appendChild(card);
  });
}

function onCardClick(e) {
  const card = e.target;
  if (lockBoard || card.classList.contains('flipped') || card.classList.contains('matched')) return;
  card.textContent = card.dataset.emoji;
  card.classList.add('flipped');
  if (!firstCard) {
    firstCard = card;
    return;
  }
  secondCard = card;
  lockBoard = true;
  checkForMatch();
}

function checkForMatch() {
  if (firstCard.dataset.emoji === secondCard.dataset.emoji) {
    firstCard.classList.add('matched');
    secondCard.classList.add('matched');
    matches++;
    if (matches === 8) {
      document.getElementById('message').textContent = 'You win!';
    }
    resetBoard();
  } else {
    setTimeout(() => {
      firstCard.textContent = '?';
      secondCard.textContent = '?';
      firstCard.classList.remove('flipped');
      secondCard.classList.remove('flipped');
      resetBoard();
    }, 1000);
  }
}

function resetBoard() {
  [firstCard, secondCard] = [null, null];
  lockBoard = false;
}

document.addEventListener('DOMContentLoaded', () => {
  createBoard();
  document.getElementById('restart').addEventListener('click', () => {
    matches = 0;
    document.getElementById('message').textContent = '';
    createBoard();
  });
});
