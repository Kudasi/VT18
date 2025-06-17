from telebot import TeleBot
from telebot.types import *
from math import prod
import json
import time
import threading

class Game:

    player1 : int  # Хрестик
    player2 : int  # Нулик

    player1_message : int
    player2_message : int

    field : dict[str, int]
    active_player : int
    history : list[str]
    
    last_turn_time : float

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.active_player = player1
        self.history = []
        self.last_turn_time = time.time()
        self.field = {
            "00": 0, "10": 0, "20": 0, 
            "01": 0, "11": 0, "21": 0, 
            "02": 0, "12": 0, "22": 0
        } # 0 - Порожня комірка
          # 1 - Нулик
          # 2 - Хрестик

with open("token.txt", "r") as f:
    bot = TeleBot(f.read().strip())

lobby_keyboard = ReplyKeyboardMarkup()
lobby_keyboard.add("Find opponent ⚔️")
lobby_keyboard.add("My statistic 📊")

game_keyboard = ReplyKeyboardMarkup()
game_keyboard.add("Stop game ⏹️")

games = {}
lobby = -1
stats = json.load(open("stats.json", "r"))

def create_message_text(game, player):
    return f"You are playing as {'X' if game.player1 == player else 'O'}\n\n" \
           f"It's {'X' if game.active_player == game.player1 else 'O'}'s turn"

def create_message_keyboard(game):
    return InlineKeyboardMarkup(row_width=3).\
    add(*[InlineKeyboardButton((" ", "O", "X")[game.field[i+j]], callback_data=i+j) for i in "012" for j in "012"])

def check_winner(game):
    # Перевірка рядків
    for i in "012":
        p = prod(game.field[j+i] for j in "012")
        if p == 1: return 1
        if p == 8: return 2
    # Перевірка ствбців
    for i in "012":
        p = prod(game.field[i+j] for j in "012")
        if p == 1: return 1
        if p == 8: return 2
    # Перевірка діагоналей
    p = prod(game.field[i+i] for i in "012")
    if p == 1: return 1
    if p == 8: return 2

    p = prod(game.field[i] for i in ("02", "11", "20"))
    if p == 1: return 1
    if p == 8: return 2

@bot.message_handler(commands=['start'])
def on_start(msg):
    if str(msg.from_user.id) not in stats: stats[str(msg.from_user.id)] = [0, 0]
    bot.send_message(msg.from_user.id, "Select action below.", reply_markup=lobby_keyboard)

@bot.message_handler(regexp="Find opponent ⚔️")
def on_find_opponent(msg):
    global lobby
    if msg.from_user.id == lobby:
        bot.send_message(msg.from_user.id, "You are already looking for an opponent!")
        return
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
        lobby = -1
    else:
        lobby = msg.from_user.id
        
@bot.message_handler(regexp="My statistic 📊")
def on_my_statistic(msg):
    bot.send_message(msg.from_user.id, "Your statistic:\n\n" \
                     f"Losses: {stats[str(msg.from_user.id)][0]}\n" \
                     f"Wins:   {stats[str(msg.from_user.id)][1]}", reply_markup=lobby_keyboard)

@bot.message_handler(regexp="Stop game ⏹️")
def on_stop_game(msg):
    game = games[msg.from_user.id]
    
    winner = game.player2 if msg.from_user.id == game.player1 else game.player1
    loser = game.player1 if winner == game.player2 else game.player2
    
    stats[str(winner)][1] += 1
    stats[str(loser)][0] += 1
    
    json.dump(stats, open("stats.json", "w"))
    
    bot.send_message(winner, "Your opponent has surrender. You won the game!", reply_markup=lobby_keyboard)
    bot.send_message(loser, "You have surrender. You lost the game!", reply_markup=lobby_keyboard)
    
    del games[game.player1]
    del games[game.player2]

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
    game.history.append(callback.data)
    if len(game.history) == 7:
        game.field[game.history[0]] = 0
        del game.history[0]
    game.active_player = game.player2 if game.active_player == game.player1 else game.player1
    game.last_turn_time = time.time()
    keyboard = create_message_keyboard(game)
    bot.edit_message_text(create_message_text(game, game.player1), game.player1, game.player1_msg, reply_markup=keyboard)
    bot.edit_message_text(create_message_text(game, game.player2), game.player2, game.player2_msg, reply_markup=keyboard)
    winner = check_winner(game)
    print(winner)
    if winner:
        bot.send_message(game.player1, f"You {'won' if winner == 2 else 'lost'} the game!", reply_markup=lobby_keyboard)
        bot.send_message(game.player2, f"You {'won' if winner == 1 else 'lost'} the game!", reply_markup=lobby_keyboard)
        del games[game.player1]
        del games[game.player2]
        stats[str(game.player1)][winner - 1] += 1
        stats[str(game.player2)][2 - winner] += 1
        with open("stats.json", "w") as f: json.dump(stats, f)        
    bot.answer_callback_query(callback.id)
    
def time_check():
    while True:
        time.sleep(1)
        games_copy = games.copy()
        for player, game in games_copy.items():
            if player != game.active_player:
                continue
            
            if time.time() - game.last_turn_time > 30:
                winner = game.player2 if game.active_player == game.player1 else game.player1
                loser = game.player1 if winner == game.player2 else game.player2
                
                stats[str(winner)][1] += 1
                stats[str(loser)][0] += 1
                
                json.dump(stats, open("stats.json", "w"))
                
                bot.send_message(winner, "You won the game due to your opponent's inactivity!", reply_markup=lobby_keyboard)
                bot.send_message(loser, "You lost the game due to inactivity!", reply_markup=lobby_keyboard)
                
                del games[game.player1]
                del games[game.player2]
                
threading.Thread(target=time_check, daemon=True).start()

bot.polling(non_stop=True)
