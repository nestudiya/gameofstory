python
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.conversationhandler import ConversationHandler
from decouple import config
from openai import OpenAI

# Настройки
BOT_TOKEN = config("BOT_TOKEN")
OPENAI_API_KEY = config("OPENAI_API_KEY")

# Инициализация OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Состояния диалога
CHOOSING, GAME_START, CHOOSING_OPTION, END = range(4)

# Список жанров
GENRES = ["Фэнтези", "Фантастика", "Детектив", "Роман", "Приключения"]

# Создание функции генерации сюжета и персонажей с помощью OpenAI
def generate_story(genre):
 response = client.completions.create(
 model="text-davinci-003",
 prompt=f"Напиши краткий сюжет рассказа в жанре {genre}.",
 max_tokens=100,
 temperature=0.7
 )
 story_text = response.choices[0].text.strip()
 return story_text

# Создание функции генерации вариантов для голосования с помощью OpenAI
def generate_options(story_text):
 response = client.completions.create(
 model="text-davinci-003",
 prompt=f"Напиши вариант продолжения сюжета:\n\n{story_text}",
 max_tokens=50,
 temperature=0.7
 )
 option = response.choices[0].text.strip()
 return option

# Обработка команды /start
def start(update: Update, context: CallbackContext) -> int:
 user = update.effective_user
 update.message.reply_text(
 f"Привет, {user.first_name}! \n\n"
 f"Я - бот, который может генерировать интересные истории! \n\n"
 f"Хочешь сыграть со мной? \n\n"
 f"Выбери жанр истории: {', '.join(GENRES)}."
 )
 return CHOOSING

# Обработка выбора жанра
def genre_chosen(update: Update, context: CallbackContext) -> int:
 user = update.effective_user
 genre = update.message.text
 if genre in GENRES:
 context.user_data['genre'] = genre
 story_text = generate_story(genre)
 option = generate_options(story_text)
 update.message.reply_text(f"Отлично! \n\n{story_text}\n\nЧто будет дальше? \n\n{option}")
 return CHOOSING_OPTION
 else:
 update.message.reply_text("Извини, я не понял. \n\nВыбери жанр истории: {', '.join(GENRES)}.")
 return CHOOSING

# Обработка выбора варианта
def option_chosen(update: Update, context: CallbackContext) -> int:
 query = update.callback_query
 user = update.effective_user
 option = query.data
 story_text = generate_story(context.user_data['genre'])
 update.message.reply_text(f"{story_text}\n\nЧто будет дальше?")
 return CHOOSING_OPTION

# Запуск бота
conv_handler = ConversationHandler(
 entry_points=[CommandHandler('start', start)],
 states={
 CHOOSING: [MessageHandler(Filters.text & ~Filters.command, genre_chosen)],
 CHOOSING_OPTION: [CallbackQueryHandler(option_chosen)],
 },
 fallbacks=[CommandHandler('start', start)]
)
dispatcher.add_handler(conv_handler)
updater.start_polling()
updater.idle()