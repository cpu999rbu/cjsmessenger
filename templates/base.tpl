<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><title>{{title or "Messenger"}}</title><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="/static/css/base.css"><link rel="stylesheet" href="/static/css/{{theme or 'light'}}.css" id="theme-link"><script src="/static/js/theme.js"></script><script src="/static/js/chat.js"></script></head>
<body data-user="{{user.username if user}}">
<div class="navbar"><span class="logo">📨 Messenger</span><button onclick="toggleTheme()">🌓</button><a href="/settings">⚙️</a></div>
<div class="content">{{!body}}</div>
</body></html>