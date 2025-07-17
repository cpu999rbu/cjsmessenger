<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Вход в Messenger</title>
  <link rel="stylesheet" href="/static/style.css" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
  <div class="container">
    <svg width="48" height="48" viewBox="0 0 24 24" fill="#4A6CF7" style="display: block; margin: 0 auto 20px;">
      <path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-3 12H7c-.55 0-1-.45-1-1s.45-1 1-1h10c.55 0 1 .45 1 1s-.45 1-1 1zm0-3H7c-.55 0-1-.45-1-1s.45-1 1-1h10c.55 0 1 .45 1 1s-.45 1-1 1zm0-3H7c-.55 0-1-.45-1-1s.45-1 1-1h10c.55 0 1 .45 1 1s-.45 1-1 1z"/>
    </svg>
    
    <h2>Вход в аккаунт</h2>

    % if error:
      <div class="error">{{error}}</div>
    % end

    <form method="post" autocomplete="off">
      <div class="input-group">
        <label for="username">Логин</label>
        <input type="text" id="username" name="username" placeholder="Введите ваш логин" required autofocus />
      </div>
      
      <div class="input-group">
        <label for="password">Пароль</label>
        <input type="password" id="password" name="password" placeholder="Введите пароль" required />
      </div>
      
      <input type="submit" value="Войти" />
    </form>

    <div class="divider">
      <span>или</span>
    </div>
    
    <p style="text-align: center; margin-top: 15px; color: #64748B;">
      Нет аккаунта? <a href="/register">Создать аккаунт</a>
    </p>
  </div>
</body>
</html>