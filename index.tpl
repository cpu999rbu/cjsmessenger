<!DOCTYPE html>
<html>
<head>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="{{'dark' if user['theme'] == 'dark' else ''}} flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900 p-4">
  <div class="bg-white dark:bg-gray-800 rounded-xl w-full max-w-md p-8 shadow-lg hover:shadow-xl transition-all duration-300">
    <header class="flex justify-between items-center mb-7 pb-4 border-b border-gray-200 dark:border-gray-700">
      <h2 class="text-2xl font-bold text-gray-800 dark:text-gray-100">Привет, {{user['username']}}!</h2>
      <nav class="flex gap-5">
        <a href="/logout" class="text-red-500 hover:text-red-600 font-semibold flex items-center gap-1">
          <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 3H4a2 2 0 00-2 2v8a2 2 0 002 2h5m6-2V5m0 0l-4 4m4-4l4 4"/>
          </svg>
          Выйти
        </a>
      </nav>
    </header>

    <h3 class="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-4">Пользователи:</h3>
    <ul class="space-y-2">
      % for u in users:
        <li class="bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900 transition-colors">
          <a href="/chat/{{u['id']}}" class="flex items-center p-3 text-gray-800 dark:text-gray-100 font-medium gap-3">
            % if u['profile_pic']:
              <img src="/{{u['profile_pic']}}" class="w-9 h-9 rounded-full" alt="{{u['username']}}">
            % else:
              <div class="w-9 h-9 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">{{u['username'][0].upper()}}</div>
            % end
            <span>{{u['username']}}</span>
          </a>
        </li>
      % end
    </ul>

    <h3 class="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-4 mt-6">Групповые чаты:</h3>
    <ul class="space-y-2">
      % for g in groups:
        <li class="bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900 transition-colors">
          <a href="/chat/group/{{g['id']}}" class="block p-3 text-gray-800 dark:text-gray-100 font-medium">{{g['name']}}</a>
        </li>
      % end
    </ul>
    <a href="/create_group" class="mt-4 block text-blue-500 hover:text-blue-600 font-medium">Создать группу</a>
  </div>
</body>
</html>