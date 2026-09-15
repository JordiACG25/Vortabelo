const mapChapeus = {
  "c": "ĉ", "g": "ĝ", "h": "ĥ", "j": "ĵ", "s": "ŝ", "u": "ŭ"
};

let lastClickTime = 0;
let lastLetterClicked = "";

function addLetter(ch) {
  if (isShaking) return;
  
  const now = Date.now();
  const esDobleToc = (now - lastClickTime < 320) && (lastLetterClicked === ch.toLowerCase());
  
  if (esDobleToc && mapChapeus[ch.toLowerCase()]) {
    // Esborra l'anterior i posa la versió amb barret
    currentInput = currentInput.slice(0, -1) + mapChapeus[ch.toLowerCase()];
    lastLetterClicked = "";
    lastClickTime = 0;
  } else {
    currentInput += ch;
    lastLetterClicked = ch.toLowerCase();
    lastClickTime = now;
  }
  
  updateInput();
}
