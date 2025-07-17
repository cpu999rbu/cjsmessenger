% include('base.tpl', title="Главная")
<div class="sidebar"><h3>Чаты</h3><ul>
% for u in users:
  % if u.id != user.id:
    <li><a href="/chat/{{u.id}}"><span class="avatar">{{u.username[0]}}</span>{{u.username}}<span class="status" id="status-{{u.id}}">• offline</span></a></li>
  % end
% end
</ul><a class="create-group-btn" href="/create_group">➕ Создать группу</a></div>
<div class="main-panel"><p>Выберите чат слева.</p></div>