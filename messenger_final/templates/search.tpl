% include('base.tpl', title="Поиск")
<h2>Поиск</h2>
<form method="get" action="/search"><input name="q" placeholder="Введите имя или ID"><button type="submit">Поиск</button></form>
% if users:
<h3>Пользователи:</h3><ul>
% for u in users: <li><a href="/chat/{{u.id}}">{{u.username}}</a></li> % end
</ul>
% end
% if groups:
<h3>Группы:</h3><ul>
% for g in groups: <li>{{g.name}}</li> % end
</ul>
% end