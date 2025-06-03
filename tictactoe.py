from telebot import TeleBot
from telebot.types import *

class Game:

    player1 : int  # Хрестик
    player2 : int  # Нулик

    player1_message : int
    player2_message : int

    field : dict[str, int]
    active_player : int

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.active_player = player1
        self.field = {
            "00": 0, "10": 0, "20": 0, 
            "01": 0, "11": 0, "21": 0, 
            "02": 0, "12": 0, "22": 0
        } # 0 - Порожня комірка
          # 1 - Нулик
          # 2 - Хрестик

with 
bot = TeleBot()

lobby_keyboard = ReplyKeyboardMarkup()
lobby_keyboard.add("Find opponent ⚔️")
lobby_keyboard.add("My statistic 📊")

game_keyboard = ReplyKeyboardMarkup()
game_keyboard.add("Stop game ⏹️")

games = {}
lobby = -1

def create_message_text(game, player):
    return f"You are playing as {'X' if game.player1 == player else 'O'}\n\n" \
           f"It's {'X' if game.active_player == game.player1 else 'O'}'s turn"

def create_message_keyboard(game):
    return InlineKeyboardMarkup(row_width=3).\
    add(*[InlineKeyboardButton((" ", "O", "X")[game.field[i+j]], callback_data=i+j) for i in "012" for j in "012"])

@bot.message_handler(commands=['start'])
def on_start(msg):
    bot.send_message(msg.from_user.id, "Select action below.", reply_markup=lobby_keyboard)

@bot.message_handler(regexp="Find opponent ⚔️")
def on_find_opponent(msg):
    global lobby
    if lobby > -1:
        player1 = msg.from_user.id
        player2 = lobby

        bot.send_message(player1, "Opponent found!", reply_markup=game_keyboard)
        bot.send_message(player2, "Opponent found!", reply_markup=game_keyboard)

        game = Game(player1, player2)
        games[player1] = game
        games[player2] = game
        
        game.player1_msg = bot.send_message(player1, create_message_text(game, player1), reply_markup=create_message_keyboard(game)).id
        game.player2_msg = bot.send_message(player2, create_message_text(game, player2), reply_markup=create_message_keyboard(game)).id

    else:
        lobby = msg.from_user.id

@bot.callback_query_handler(func=lambda a: True)
def on_button_press(callback):
    if callback.from_user.id not in games:
        bot.answer_callback_query(callback.id, "You are not in a game!")
        return

    game = games[callback.from_user.id]

    if game.active_player != callback.from_user.id:
        bot.answer_callback_query(callback.id, "It's not your turn!")
        return
    
    if game.field[callback.data] != 0:
        bot.answer_callback_query(callback.id, "This cell is already occupied!")
        return
    
    game.field[callback.data] = 2 if game.active_player == game.player1 else 1
    game.active_player = game.player2 if game.active_player == game.player1 else game.player1
    keyboard = create_message_keyboard(game)
    bot.edit_message_text(create_message_text(game, game.player1), game.player1, game.player1_msg, reply_markup=keyboard)
    bot.edit_message_text(create_message_text(game, game.player2), game.player2, game.player2_msg, reply_markup=keyboard)
    bot.answer_callback_query(callback.id, "Move accepted!")    




bot.polling(non_stop=True)
