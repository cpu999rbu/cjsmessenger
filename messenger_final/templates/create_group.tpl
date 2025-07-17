% include('base.tpl', title="Создать группу")
<h2>Создать группу</h2>
<form method="post" action="/create_group">
  <input name="group_name" placeholder="Название группы">
  <button type="submit">Создать</button>
</form>