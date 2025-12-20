document.querySelectorAll('.clicked').forEach(item => {
  item.addEventListener('click', event => {
      item.classList.toggle('clicked');
  });
});
