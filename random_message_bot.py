import telebot             # Імпортування бібліотеки API Telegram бота
import random             # Імпортування модуля для випадкового вибору

bot = telebot.TeleBot("TOKEN")  # Створення екземпляру бота з API токеном
users = []                      # Ініціалізація порожнього списку для зберігання ID користувачів

@bot.message_handler(commands=['start'])  # Декоратор для обробки команди /start
def on_start(message):                   # Функція, яка обробляє команду start
    users.append(message.from_user.id)   # Додавання ID користувача до списку users, коли вони запускають бота

@bot.message_handler(func=lambda a: True)  # Декоратор для обробки всіх текстових повідомлень
def on_message(message):                   # Функція, яка обробляє всі повідомлення
    random_user = random.choice(users)     # Вибір випадкового користувача зі списку users
    bot.send_message(random_user, message.text)  # Надсилання отриманого повідомлення випадковому користувачу

bot.polling(non_stop=True)                # Запуск бота та підтримка його безперервної роботи
