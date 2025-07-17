% include('base.tpl', title="Чат с " + recipient.username)
<div class="chat-wrapper">
<div class="chat-header"><span class="avatar">{{recipient.username[0]}}</span><div><h2>{{recipient.username}}</h2><span class="status" id="status-{{recipient.id}}">• offline</span></div></div>
<div class="messages" id="messages">
% for msg in messages:
  <div class="message {% if msg.user_id==user.id %}me{% else %}you{% end %}">
    % if '[voice]' in msg.content:
      <audio controls src="/{{msg.content.replace('[voice]', '')}}"></audio>
    % elif '[video]' in msg.content:
      <video controls src="/{{msg.content.replace('[video]', '')}}" width="200"></video>
    % else:
      <p>{{msg.content}}</p>
    % end
    <span class="time">{{msg.timestamp}}</span>
  </div>
% end
</div>
<div class="typing-indicator" id="typing-{{recipient.id}}"></div>
<form id="chat-form" onsubmit="return sendMessage(event, {{recipient.id}});">
  <input name="message" autocomplete="off" id="msg-input" oninput="typing({{recipient.id}})" placeholder="Введите сообщение">
  <button type="submit">➡️</button>
</form>
<div class="media-controls">
  <button onclick="startRecording()">🎙️</button><button onclick="stopRecording()">⏹️</button>
  <form id="voice-form" method="post" enctype="multipart/form-data" action="/upload_voice"><input name="voice" id="voice-input" type="file" style="display:none;"></form>
  <button onclick="startVideo()">🎥</button><button onclick="stopVideo()">⏹️</button>
  <form id="video-form" method="post" enctype="multipart/form-data" action="/upload_video"><input name="video" id="video-input" type="file" style="display:none;"></form>
</div>