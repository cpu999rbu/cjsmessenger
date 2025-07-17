<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Чат с {{peer['username']}}</title>
  <link rel="stylesheet" href="/static/style.css">
  <script src="/static/main.js"></script>
</head>
<body>
  <div class="chat-container">
    <div class="chat-header">
      <div class="user-avatar">{{peer['username'][0].upper()}}</div>
      <h2>{{peer['username']}}</h2>
      <a href="/" class="back">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M15 9H4m0 0l4-4m-4 4l4 4"/>
        </svg>
        Назад
      </a>
    </div>

    <div class="chat-messages" id="messages">
      % for m in messages:
        <div class="message {{'self' if m['sender_id'] == user['id'] else 'peer'}}">
          <p>{{m['content']}}</p>
          <small>{{m['timestamp']}}</small>
        </div>
      % end
    </div>

    <form class="chat-form" method="POST">
      <input type="text" id="message-input" name="content" placeholder="Введите сообщение..." required>
      <button type="submit" id="send-btn">Отправить</button>
    </form>
  </div>
</body>
</html>