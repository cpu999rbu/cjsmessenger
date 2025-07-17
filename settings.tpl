<!DOCTYPE html>
<html>
<head>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="{{'dark' if user['theme'] == 'dark' else ''}} flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900 p-4">
  <div class="bg-white dark:bg-gray-800 rounded-xl w-full max-w-md p-8 shadow-lg">
    <h2 class="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-6">Настройки аккаунта</h2>
    % if error:
      <div class="bg-red-100 text-red-600 p-3 rounded-lg mb-5 font-medium">{{error}}</div>
    % end
    <form method="POST" enctype="multipart/form-data" class="space-y-5">
      <div>
        <label for="current_password" class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">Текущий пароль</label>
        <input type="password" name="current_password" id="current_password" class="w-full p-3 rounded-xl border border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring focus:ring-blue-200 transition-all" required>
      </div>
      <div>
        <label for="username" class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">Новый логин</label>
        <input type="text" name="username" id="username" value="{{user['username']}}" class="w-full p-3 rounded-xl border border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring focus:ring-blue-200 transition-all">
      </div>
      <div>
        <label for="new_password" class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">Новый пароль</label>
        <input type="password" name="new_password" id="new_password" class="w-full p-3 rounded-xl border border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring focus:ring-blue-200 transition-all">
      </div>
      <div>
        <label for="profile_pic" class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">Фото профиля</label>
        <input type="file" name="profile_pic" accept="image/*" class="mt-2 text-gray-600 dark:text-gray-300">
      </div>
      <div>
        <label for="theme" class="block text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">Тема</label>
        <select name="theme" id="theme" class="w-full p-3 rounded-xl border border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring focus:ring-blue-200 transition-all">
          <option value="light" {{'selected' if user['theme'] == 'light' else ''}}>Светлая</option>
          <option value="dark" {{'selected' if user['theme'] == 'dark' else ''}}>Темная</option>
        </select>
      </div>
      <button type="submit" class="w-full p-3 bg-blue-500 text-white rounded-xl font-semibold hover:bg-blue-600 transition-all">Сохранить</button>
    </form>
    <a href="/" class="block text-center mt-5 text-blue-500 hover:text-blue-600 font-medium">Назад</a>
  </div>
</body>
</html>