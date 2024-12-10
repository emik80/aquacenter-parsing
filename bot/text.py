# Main Menu commands
MENU_COMMANDS = {
    '/start':   'Початок роботи',
    '/help':    'Допомога',
    '/cancel':  'Скасувати',
}

# Bot messages
BOT_MESSAGES = {
    'start': 'Hi 👋',
    'help': f'ℹ Бот призначений для парсингу товарів. Для отримання результату вам потрібно ввести URL для парсингу, '
            f'а також категорію, в яку будуть додані товари.\n\n'
            f'За декілька хвилин (в залежності від кількості товарів), які потрібно буде опрацювати, '
            f'ви отримаєте підготовлений для імпорту файл з товарами.\n\n'
            f'Одночасно може виконуватись лише одна задача. '
            f'Перед введенням нових запросів дочекайтеся завершення попередньої задачі',
    'task_in_progress': '⚠ Вже виконується інша задача парсингу. Дочекайтеся її завершеня.',
    'source url': '🔽 Введіть URL',
    'target category': '🔽 Введіть категорію, в яку будуть додаватися товари',
    'cancel_selected': '🔴 Скасовано!',
    'error': '⚠ Виникла помилка!\nСпробуйте команду /start чи /help ',
    'unknown': f'Невідома команда 🥲\n'
               f'Спробуйте команду /start чи /help ',
    'unknown_user': '⚠ Access denied!'
}

# Admin messages
ADMIN_MESSAGES = {
    'hello': '😎 Yes my Lord!',
    'input_id': '🔽 Enter User ID',
    'done': 'Process completed',
    'logout': 'You are logged out of administrator mode, type /start to work with bot in standard mode',
    'not_admin': '⚠ You do not have permission to do this action!'
}
