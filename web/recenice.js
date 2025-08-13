const data = [
  "One day, a little mouse was walking through the forest.",
  "Puss in Boots was clever and smart.",
  "The little mermaid dreamed of living on land.",
  "The ugly duckling grew into a beautiful swan.",
  "In the forest lived a bear named Winnie the Pooh.",
  "Santa Claus brings gifts to children all over the world.",
  "The little princess loved playing in the mud.",
  "The three little pigs built three different houses.",
  "The Little Prince loved watching sunsets.",
  "The little ladybug overheard the plans of two suspicious characters.",
  "Alice followed the white rabbit and fell into a rabbit hole.",
  "The Gruffalo is a scary monster with tusks and claws.",
  "Little Red Riding Hood wore a red hood and went to visit her grandmother.",
  "Peter Pan could fly and never grew up.",
  "Snow White lived with seven dwarfs in a small cottage.",
  "The big bad wolf blew and the straw house collapsed.",
  "Hansel and Gretel found a candy house in the middle of the forest.",
  "Goldilocks had long golden hair and loved wandering through the forest.",
  "Pinocchio was a wooden puppet who wanted to become a real boy.",
  "The little blue locomotive believed it could climb over the big hill."
];

function showRandomSentence() {
  const sentence = data[Math.floor(Math.random() * data.length)];
  document.getElementById('sentence').textContent = sentence;
}

document.addEventListener('DOMContentLoaded', () => {
  showRandomSentence();
  document.getElementById('next').addEventListener('click', showRandomSentence);
});
