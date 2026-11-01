'use strict';
const fitButton = document.getElementById('fit');
const actualButton = document.getElementById('actual');
function setScale(actual) {
  document.body.classList.toggle('actual', actual);
  fitButton.setAttribute('aria-pressed', String(!actual));
  actualButton.setAttribute('aria-pressed', String(actual));
}
fitButton.addEventListener('click', () => setScale(false));
actualButton.addEventListener('click', () => setScale(true));
function replay(id) {
  const element = document.getElementById(id);
  element.classList.remove('play');
  void element.offsetWidth;
  element.classList.add('play');
}
document.getElementById('replay').addEventListener('click', () => replay('reveal'));
document.getElementById('sweep').addEventListener('click', () => replay('curtain'));
document.querySelectorAll('.accordion-demo details').forEach((item) => {
  item.addEventListener('toggle', () => {
    if (item.open) {
      document.querySelectorAll('.accordion-demo details').forEach((other) => {
        if (other !== item) other.open = false;
      });
    }
  });
});
