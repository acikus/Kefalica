const data = [
  { image: 'recenice_assets/MALMIS.png', text: 'One day, a little mouse was walking through the forest.' },
  { image: 'recenice_assets/MACCIZ.png', text: 'Puss in Boots was clever and smart.' },
  { image: 'recenice_assets/MSIREN.png', text: 'The little mermaid dreamed of living on land.' },
  { image: 'recenice_assets/RUZPAC.png', text: 'The ugly duckling grew into a beautiful swan.' },
  { image: 'recenice_assets/VINIPU.png', text: 'In the forest lived a bear named Winnie the Pooh.' },
  { image: 'recenice_assets/DEDMRA.png', text: 'Santa Claus brings gifts to children all over the world.' },
  { image: 'recenice_assets/MALPRI.png', text: 'The little princess loved playing in the mud.' },
  { image: 'recenice_assets/TRIPRA.png', text: 'The three little pigs built three different houses.' },
  { image: 'recenice_assets/MPRINC.png', text: 'The Little Prince loved watching sunsets.' },
  { image: 'recenice_assets/MALBUB.png', text: 'The little ladybug overheard the plans of two suspicious characters.' },
  { image: 'recenice_assets/MALISA.png', text: 'Alice followed the white rabbit and fell into a rabbit hole.' },
  { image: 'recenice_assets/GROZON.png', text: 'The Gruffalo is a scary monster with tusks and claws.' },
  { image: 'recenice_assets/CRVENK.png', text: 'Little Red Riding Hood wore a red hood and went to visit her grandmother.' },
  { image: 'recenice_assets/PETPAN.png', text: 'Peter Pan could fly and never grew up.' },
  { image: 'recenice_assets/SNEPAT.png', text: 'Snow White lived with seven dwarfs in a small cottage.' },
  { image: 'recenice_assets/ZLIVUK.png', text: 'The big bad wolf blew and the straw house collapsed.' },
  { image: 'recenice_assets/IVIMAR.png', text: 'Hansel and Gretel found a candy house in the middle of the forest.' },
  { image: 'recenice_assets/ZLATOK.png', text: 'Goldilocks had long golden hair and loved wandering through the forest.' },
  { image: 'recenice_assets/PINOKI.png', text: 'Pinocchio was a wooden puppet who wanted to become a real boy.' },
  { image: 'recenice_assets/MALLOK.png', text: 'The little blue locomotive believed it could climb over the big hill.' }
];

let currentIndex = 0;
let currentSentence = [];

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

function randomColor() {
  const colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightpink', 'orange', 'lavender', 'tomato'];
  return colors[Math.floor(Math.random() * colors.length)];
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('prevBtn').addEventListener('click', showPrevious);
  document.getElementById('nextBtn').addEventListener('click', showNext);
  document.getElementById('finishBtn').addEventListener('click', finishGame);
  showSentence(currentIndex);
});

function showSentence(index) {
  const item = data[index];
  document.getElementById('image').src = item.image;
  currentSentence = item.text.toUpperCase().split(' ');
  const shuffled = shuffle([...currentSentence]);
  const available = document.getElementById('available');
  const selected = document.getElementById('selected');
  available.innerHTML = '';
  selected.innerHTML = '';
  shuffled.forEach(word => {
    const btn = document.createElement('button');
    btn.textContent = word;
    btn.className = 'word';
    btn.style.backgroundColor = randomColor();
    btn.addEventListener('click', () => toggleWord(btn));
    available.appendChild(btn);
  });
  document.getElementById('nextBtn').disabled = true;
  updateProgress();
}

function toggleWord(btn) {
  const parent = btn.parentElement.id;
  if (parent === 'available') {
    document.getElementById('selected').appendChild(btn);
  } else {
    document.getElementById('available').appendChild(btn);
  }
  checkSentence();
}

function checkSentence() {
  const selectedWords = Array.from(document.getElementById('selected').children).map(b => b.textContent);
  if (selectedWords.length !== currentSentence.length) {
    document.getElementById('nextBtn').disabled = true;
    return;
  }
  const correct = selectedWords.join(' ') === currentSentence.join(' ');
  document.getElementById('nextBtn').disabled = !correct;
}

function showPrevious() {
  if (currentIndex > 0) {
    currentIndex--;
    showSentence(currentIndex);
  }
}

function showNext() {
  if (currentIndex < data.length - 1) {
    currentIndex++;
    showSentence(currentIndex);
  }
}

function updateProgress() {
  document.getElementById('progress').textContent = `Sentence ${currentIndex + 1}/${data.length}`;
}

function finishGame() {
  alert('Game finished!');
}
