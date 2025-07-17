<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Регистрация в Messenger</title>
  <link rel="stylesheet" href="/static/style.css" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
  <div class="container">
    <svg width="48" height="48" viewBox="0 0 24 24" fill="#4A6CF7" style="display: block; margin: 0 auto 20px;">
      <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
    </svg>
    
    <h2>Создать аккаунт</h2>

    % if error:
      <div class="error">{{error}}</div>
    % end

    <form method="post" autocomplete="off">
      <div class="input-group">
        <label for="username">Логин</label>
        <input type="text" id="username" name="username" placeholder="Придумайте логин" required autofocus />
      </div>
      
      <div class="input-group">
        <label for="password">Пароль</label>
        <input type="password" id="password" name="password" placeholder="Придумайте пароль" required />
      </div>
      
      <input type="submit" value="Зарегистрироваться" />
    </form>

    <div class="divider">
      <span>или</span>
    </div>
    
    <p style="text-align: center; margin-top: 15px; color: #64748B;">
      Уже есть аккаунт? <a href="/login">Войти</a>
    </p>
  </div>
</body>
</html>