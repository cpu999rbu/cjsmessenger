% include('base.tpl', title="Регистрация")
<form action="/register" method="post">
  % if error: <p style="color:red">{{error}}</p> % end
  <input name="username" placeholder="Имя">
  <input name="password" type="password" placeholder="Пароль">
  <button type="submit">Зарегистрироваться</button>
</form>
<p><a href="/login">Войти</a></p>