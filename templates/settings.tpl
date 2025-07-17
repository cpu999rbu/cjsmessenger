% include('base.tpl', title="Настройки")
<h2>Настройки аккаунта</h2>
<div class="tabs">
  <button onclick="openTab('profile')" class="tab-button">Профиль</button>
  <button onclick="openTab('privacy')" class="tab-button">Приватность</button>
  <button onclick="openTab('theme')" class="tab-button">Тема</button>
</div>
<div id="profile" class="tab-content">
  <h3>Профиль</h3>
  <form method="post" action="/settings/profile">
    <input name="username" value="{{user.username}}" placeholder="Имя пользователя">
    <button type="submit">Сохранить</button>
  </form>
</div>
<div id="privacy" class="tab-content" style="display:none">
  <h3>Приватность</h3><p>Настройки приватности...</p>
</div>
<div id="theme" class="tab-content" style="display:none">
  <h3>Тема</h3><button onclick="toggleTheme()">Сменить тему</button>
</div>
<script>
function openTab(id){document.querySelectorAll('.tab-content').forEach(el=>el.style.display='none');document.getElementById(id).style.display='block';}
</script>