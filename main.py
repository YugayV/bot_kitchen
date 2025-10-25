import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from translations import get_translation
import sqlite3
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class SimpleFoodBot:
    def __init__(self):
        self.db_path = os.getenv('DATABASE_PATH', 'food_bot.db')
        self.init_database()
    
    def init_database(self):
        """Простая инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'ru'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name_ru TEXT,
                name_ko TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dishes (
                id INTEGER PRIMARY KEY,
                name_ru TEXT,
                name_ko TEXT,
                price INTEGER
            )
        ''')
        
        # Добавляем тестовые данные
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            categories = [
                (1, 'Первые блюда', '첫 번째 요리'),
                (2, 'Вторые блюда', '두 번째 요리'),
                (3, 'Стейки', '스테이크')
            ]
            cursor.executemany("INSERT INTO categories (id, name_ru, name_ko) VALUES (?, ?, ?)", categories)
            
            dishes = [
                (1, 1, 'Борщ', '보르시', 250),
                (2, 1, 'Солянка', '솔랸카', 280),
                (3, 2, 'Тушенка', '스튜', 350),
                (4, 3, 'Томогавк', '토마호크', 1200)
            ]
            cursor.executemany("INSERT INTO dishes (id, category_id, name_ru, name_ko, price) VALUES (?, ?, ?, ?, ?)", dishes)
        
        conn.commit()
        conn.close()
        logging.info("✅ База данных готова")
    
    def get_user_language(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 'ru'
    
    def set_user_language(self, user_id, language):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)
        ''', (user_id, language))
        conn.commit()
        conn.close()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        language = self.get_user_language(user_id)
        
        keyboard = [
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
            [InlineKeyboardButton("🛒 " + get_translation(language, 'cart'), callback_data="cart")],
            [InlineKeyboardButton("🌐 한국어", callback_data="lang_ko"),
             InlineKeyboardButton("🌐 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("📞 " + get_translation(language, 'contacts'), callback_data="contacts")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            get_translation(language, 'welcome'),
            reply_markup=reply_markup
        )
    
    async def handle_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = query.data.split('_')[1]
        
        self.set_user_language(user_id, language)
        
        keyboard = [
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
            [InlineKeyboardButton("🛒 " + get_translation(language, 'cart'), callback_data="cart")],
            [InlineKeyboardButton("🌐 한국어", callback_data="lang_ko"),
             InlineKeyboardButton("🌐 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("📞 " + get_translation(language, 'contacts'), callback_data="contacts")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_translation(language, 'language_changed'),
            reply_markup=reply_markup
        )
    
    async def handle_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name_ru, name_ko FROM categories")
        categories = cursor.fetchall()
        conn.close()
        
        keyboard = []
        for cat_id, name_ru, name_ko in categories:
            name = name_ko if language == 'ko' else name_ru
            keyboard.append([InlineKeyboardButton(name, callback_data=f"cat_{cat_id}")])
        
        keyboard.append([InlineKeyboardButton(get_translation(language, 'back'), callback_data="back")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_translation(language, 'choose_category'),
            reply_markup=reply_markup
        )
    
    def setup_handlers(self, application):
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.handle_language, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.handle_menu, pattern="^menu$"))

async def main():
    # Получаем токен из переменных окружения
    token = os.getenv('BOT_TOKEN')
    if not token:
        logging.error("❌ BOT_TOKEN не найден в переменных окружения")
        return
    
    application = Application.builder().token(token).build()
    
    bot = SimpleFoodBot()
    bot.setup_handlers(application)
    
    logging.info("🚀 Бот запущен!")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())