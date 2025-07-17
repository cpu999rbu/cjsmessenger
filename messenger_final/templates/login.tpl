% include('base.tpl', title="Вход")
<form action="/login" method="post">
  % if error: <p style="color:red">{{error}}</p> % end
  <input name="username" placeholder="Имя">
  <input name="password" type="password" placeholder="Пароль">
  <button type="submit">Войти</button>
</form>
<p><a href="/register">Регистрация</a></p>