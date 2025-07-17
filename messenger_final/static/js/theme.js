document.addEventListener('DOMContentLoaded',() => {
  let current = localStorage.getItem('theme')||'light';
  document.getElementById('theme-link').href=`/static/css/${current}.css`;
  window.toggleTheme=()=>{ current=(current==='light')?'dark':'light'; document.getElementById('theme-link').href=`/static/css/${current}.css`; localStorage.setItem('theme',current); };
});