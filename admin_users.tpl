<!DOCTYPE html>
<html>
<head>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="{{'dark' if user['theme'] == 'dark' else ''}} flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900 p-4">
  <div class="bg-white dark:bg-gray-800 rounded-xl w-full max-w-4xl p-8 shadow-lg">
    <h2 class="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-6">Управление пользователями</h2>
    <table class="w-full">
      <thead>
        <tr class="bg-gray-100 dark:bg-gray-700">
          <th class="p-3 text-left">ID</th>
          <th class="p-3 text-left">Логин</th>
          <th class="p-3 text-left">Админ</th>
          <th class="p-3 text-left">Действия</th>
        </tr>
      </thead>
      <tbody>
        % for u in users:
          <tr class="border-b border-gray-200 dark:border-gray-700">
            <td class="p-3">{{u['id']}}</td>
            <td class="p-3">{{u['username']}}</td>
            <td class="p-3">{{'Да' if u['is_admin'] else 'Нет'}}</td>
            <td class="p-3">
              <a href="/admin/user/{{u['id']}}/edit" class="text-blue-500 hover:text-blue-600">Редактировать</a>
              <a href="/admin/user/{{u['id']}}/delete" class="text-red-500 hover:text-red-600 ml-3">Удалить</a>
            </td>
          </tr>
        % end
      </tbody>
    </table>
    <a href="/" class="block text-center mt-5 text-blue-500 hover:text-blue-600 font-medium">Назад</a>
  </div>
</body>
</html>