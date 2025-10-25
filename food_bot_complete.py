import logging
import json
import os
import sqlite3
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
import speech_recognition as sr
from pydub import AudioSegment
import io
import asyncio
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]

class FoodBot:
    def __init__(self):
        self.db_path = "food_bot.db"
        self.init_database()
        self.setup_google_sheets()
        self.user_states = {}
        self.recognizer = sr.Recognizer()

    def setup_google_sheets(self):
        """Настройка подключения к Google Sheets"""
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            creds = Credentials.from_service_account_file(
                os.getenv('GOOGLE_SHEETS_CREDENTIALS'),
                scopes=scopes
            )
            
            self.gc = gspread.authorize(creds)
            self.sheet_name = os.getenv('SHEET_NAME', 'FoodOrders')
            
            # Пытаемся открыть таблицу или создать новую
            try:
                self.sheet = self.gc.open(self.sheet_name).sheet1
            except gspread.SpreadsheetNotFound:
                # Создаем новую таблицу
                spreadsheet = self.gc.create(self.sheet_name)
                self.sheet = spreadsheet.sheet1
                
                # Заголовки столбцов
                headers = [
                    'ID заказа', 'Дата', 'Имя клиента', 'Телефон', 'Адрес',
                    'Сумма', 'Статус', 'Статус оплаты', 'Товары', 'ID пользователя'
                ]
                self.sheet.append_row(headers)
                
                # Даем доступ для просмотра
                spreadsheet.share(None, perm_type='anyone', role='reader')
                
            logging.info("Google Sheets подключен успешно")
            
        except Exception as e:
            logging.error(f"Ошибка подключения к Google Sheets: {e}")
            self.sheet = None

    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица категорий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                display_order INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица блюд
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                weight TEXT,
                calories TEXT,
                storage_conditions TEXT,
                cooking_method TEXT,
                price INTEGER NOT NULL,
                image_path TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Таблица заказов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_name TEXT,
                phone TEXT,
                address TEXT,
                total_amount INTEGER,
                status TEXT DEFAULT 'pending',
                payment_status TEXT DEFAULT 'unpaid',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица элементов заказа
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                dish_id INTEGER,
                quantity INTEGER,
                price INTEGER,
                FOREIGN KEY (order_id) REFERENCES orders (id),
                FOREIGN KEY (dish_id) REFERENCES dishes (id)
            )
        ''')
        
        # Таблица реквизитов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank_name TEXT,
                account_number TEXT,
                recipient_name TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица платежей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                amount INTEGER,
                screenshot_path TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders (id)
            )
        ''')
        
        # Начальные данные
        cursor.execute('SELECT COUNT(*) FROM categories')
        if cursor.fetchone()[0] == 0:
            initial_categories = [
                ('Первые блюда', 1),
                ('Вторые блюда', 2),
                ('Маринованные Стэйки', 3)
            ]
            cursor.executemany('INSERT INTO categories (name, display_order) VALUES (?, ?)', initial_categories)
            
            # Начальные реквизиты
            cursor.execute('''
                INSERT INTO payment_details (bank_name, account_number, recipient_name) 
                VALUES (?, ?, ?)
            ''', ('Тинькофф', '0000 0000 0000 0000', 'Иванов Иван Иванович'))
            
            # Пример блюд
            sample_dishes = [
                (1, 'Борщ', 'Ароматный борщ со сметаной', '400г', '150 ккал', 
                 '+4°C', 'Разогреть 5 минут', 250, 'images/borscht.jpg'),
                (2, 'Тушенка говяжья', 'Нежная тушеная говядина', '300г', '200 ккал',
                 '+4°C', 'Разогреть 3 минуты', 350, 'images/beef_stew.jpg'),
                (3, 'Томогавк', 'Сочный стейк томагавк', '500г', '350 ккал',
                 '-18°C', 'Жарить 8-10 минут', 1200, 'images/tomahawk.jpg')
            ]
            cursor.executemany('''
                INSERT INTO dishes (category_id, name, description, weight, calories, 
                storage_conditions, cooking_method, price, image_path) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_dishes)
        
        conn.commit()
        conn.close()

    async def convert_voice_to_text(self, voice_file):
        """Конвертирование голосового сообщения в текст"""
        try:
            # Скачиваем голосовое сообщение
            voice_data = await voice_file.download_as_bytearray()
            
            # Конвертируем ogg в wav
            audio = AudioSegment.from_ogg(io.BytesIO(voice_data))
            wav_data = io.BytesIO()
            audio.export(wav_data, format="wav")
            wav_data.seek(0)
            
            # Распознаем речь
            with sr.AudioFile(wav_data) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language="ru-RU")
                return text
                
        except Exception as e:
            logging.error(f"Ошибка распознавания голоса: {e}")
            return None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        keyboard = [
            [InlineKeyboardButton("🍽️ Меню", callback_data="menu")],
            [InlineKeyboardButton("🛒 Корзина", callback_data="view_cart")],
            [InlineKeyboardButton("📞 Контакты", callback_data="contacts")],
            [InlineKeyboardButton("🎤 Голосовой заказ", callback_data="voice_order")]
        ]
        
        if user_id in ADMIN_IDS:
            keyboard.append([InlineKeyboardButton("⚙️ Админ-панель", callback_data="admin_panel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🍖 Здравствуйте! Вас приветствует компания ФУД!\n"
            "Благодарим за то что выбираете нас!\n\n"
            "Вы можете:\n"
            "• Выбрать блюда из меню 🍽️\n"
            "• Сделать заказ голосом 🎤\n"
            "• Посмотреть корзину 🛒\n\n"
            "Выберите действие:",
            reply_markup=reply_markup
        )

    async def voice_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало голосового заказа"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🎤 **Голосовой заказ**\n\n"
            "Нажмите на микрофон и продиктуйте ваш заказ.\n"
            "Например: *'Два борща, одну тушенку и стейк томагавк'*\n\n"
            "Я постараюсь распознать и добавить в корзину."
        )
        
        context.user_data['waiting_voice'] = True

    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка голосовых сообщений"""
        if not context.user_data.get('waiting_voice'):
            return
            
        voice = update.message.voice
        voice_file = await voice.get_file()
        
        # Показываем что обрабатываем
        processing_msg = await update.message.reply_text("🔄 Обрабатываю голосовое сообщение...")
        
        # Конвертируем голос в текст
        text = await self.convert_voice_to_text(voice_file)
        
        if text:
            await processing_msg.edit_text(f"🎤 Распознано: *{text}*", parse_mode='Markdown')
            
            # Парсим заказ и добавляем в корзину
            result = await self.parse_voice_order(text, context)
            await update.message.reply_text(result)
        else:
            await processing_msg.edit_text("❌ Не удалось распознать голос. Попробуйте еще раз.")
        
        context.user_data['waiting_voice'] = False

    async def parse_voice_order(self, text: str, context: ContextTypes.DEFAULT_TYPE):
        """Парсинг голосового заказа и добавление в корзину"""
        try:
            # Простой парсинг (можно улучшить с помощью NLP)
            text_lower = text.lower()
            added_items = []
            
            # Список блюд для поиска
            dishes = self.get_all_dishes()
            
            for dish_id, dish_name, dish_price in dishes:
                dish_name_lower = dish_name.lower()
                
                # Ищем упоминание блюда в тексте
                if dish_name_lower in text_lower:
                    # Пытаемся найти количество
                    quantity = 1
                    words = text_lower.split()
                    
                    for i, word in enumerate(words):
                        if word.isdigit() and i < len(words) - 1:
                            if words[i + 1] in dish_name_lower.split():
                                quantity = int(word)
                                break
                    
                    # Добавляем в корзину
                    if 'cart' not in context.user_data:
                        context.user_data['cart'] = {}
                    
                    cart = context.user_data['cart']
                    dish_key = str(dish_id)
                    
                    if dish_key in cart:
                        cart[dish_key]['quantity'] += quantity
                    else:
                        cart[dish_key] = {
                            'name': dish_name,
                            'price': dish_price,
                            'quantity': quantity
                        }
                    
                    added_items.append(f"{dish_name} x{quantity}")
            
            if added_items:
                items_text = "\n".join(f"• {item}" for item in added_items)
                return f"✅ Добавлено в корзину:\n{items_text}\n\nПроверьте корзину 🛒"
            else:
                return "❌ Не удалось найти блюда в заказе. Попробуйте выбрать из меню 🍽️"
                
        except Exception as e:
            logging.error(f"Ошибка парсинга голосового заказа: {e}")
            return "❌ Произошла ошибка. Попробуйте выбрать блюда из меню 🍽️"

    def get_all_dishes(self):
        """Получить все блюда"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, price FROM dishes')
        dishes = cursor.fetchall()
        conn.close()
        return dishes

    async def handle_payment_screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка скриншота оплаты"""
        user_id = update.effective_user.id
        
        if context.user_data.get('waiting_payment'):
            photo = update.message.photo[-1]
            file = await photo.get_file()
            
            # Сохраняем скриншот
            file_path = f"payment_screenshots/{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            os.makedirs("payment_screenshots", exist_ok=True)
            await file.download_to_drive(file_path)
            
            # Обновляем статус заказа
            order_id = context.user_data['current_order_id']
            self.update_order_payment_status(order_id, 'paid', file_path)
            
            # Уведомляем администраторов
            await self.notify_admins_about_payment(context.bot, order_id, user_id, file_path)
            
            await update.message.reply_text(
                "✅ Скриншот оплаты получен! Мы проверяем платеж и скоро подтвердим ваш заказ.\n"
                "Спасибо за заказ! ❤️"
            )
            
            context.user_data['waiting_payment'] = False

    async def notify_admins_about_payment(self, bot, order_id, user_id, screenshot_path):
        """Уведомление администраторов об оплате"""
        order_info = self.get_order_info(order_id)
        
        if not order_info:
            return
        
        message_text = (
            "💰 **НОВАЯ ОПЛАТА!**\n\n"
            f"📋 Заказ №{order_id}\n"
            f"👤 Клиент: {order_info['user_name']}\n"
            f"📞 Телефон: {order_info['phone']}\n"
            f"🏠 Адрес: {order_info['address']}\n"
            f"💵 Сумма: {order_info['total_amount']}₽\n\n"
            "✅ Ожидает подтверждения"
        )
        
        for admin_id in ADMIN_IDS:
            try:
                # Отправляем текст
                await bot.send_message(admin_id, message_text)
                
                # Отправляем скриншот
                with open(screenshot_path, 'rb') as photo:
                    await bot.send_photo(admin_id, photo, caption="Скриншот оплаты")
                
                # Кнопки для подтверждения
                keyboard = [
                    [
                        InlineKeyboardButton("✅ Подтвердить оплату", 
                                          callback_data=f"confirm_payment_{order_id}"),
                        InlineKeyboardButton("❌ Отклонить", 
                                          callback_data=f"reject_payment_{order_id}")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await bot.send_message(
                    admin_id,
                    "Подтвердите получение оплаты:",
                    reply_markup=reply_markup
                )
                
            except Exception as e:
                logging.error(f"Ошибка уведомления админа {admin_id}: {e}")

    async def confirm_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение оплаты администратором"""
        query = update.callback_query
        await query.answer()
        
        order_id = int(query.data.split('_')[-1])
        
        # Обновляем статус в базе
        self.update_order_payment_status(order_id, 'confirmed')
        
        # Уведомляем пользователя
        order_info = self.get_order_info(order_id)
        if order_info:
            try:
                await context.bot.send_message(
                    order_info['user_id'],
                    "🎉 **Ваш платеж подтвержден!**\n\n"
                    "Заказ передан на кухню. Скоро с вами свяжутся для уточнения деталей доставки.\n"
                    "Спасибо за заказ! ❤️"
                )
            except Exception as e:
                logging.error(f"Ошибка уведомления пользователя: {e}")
        
        await query.edit_message_text(f"✅ Оплата для заказа #{order_id} подтверждена!")

    def update_order_payment_status(self, order_id, status, screenshot_path=None):
        """Обновление статуса оплаты"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE orders SET payment_status = ? WHERE id = ?
        ''', (status, order_id))
        
        if screenshot_path:
            cursor.execute('''
                INSERT INTO payments (order_id, amount, screenshot_path, status)
                VALUES (?, ?, ?, ?)
            ''', (order_id, self.get_order_total(order_id), screenshot_path, status))
        
        conn.commit()
        conn.close()
        
        # Обновляем Google Sheets
        self.update_google_sheets(order_id)

    def update_google_sheets(self, order_id):
        """Обновление Google Sheets"""
        if not self.sheet:
            return
            
        try:
            order_info = self.get_order_info(order_id)
            if not order_info:
                return
            
            # Форматируем данные для таблицы
            order_items = self.get_order_items(order_id)
            items_text = ", ".join([f"{item['name']} x{item['quantity']}" for item in order_items])
            
            row_data = [
                order_id,
                order_info['created_at'],
                order_info['user_name'],
                order_info['phone'],
                order_info['address'],
                order_info['total_amount'],
                order_info['status'],
                order_info['payment_status'],
                items_text,
                order_info['user_id']
            ]
            
            # Ищем существующую запись
            try:
                cell = self.sheet.find(str(order_id))
                # Обновляем существующую строку
                for i, value in enumerate(row_data, 1):
                    self.sheet.update_cell(cell.row, i, value)
            except gspread.exceptions.CellNotFound:
                # Добавляем новую строку
                self.sheet.append_row(row_data)
                
        except Exception as e:
            logging.error(f"Ошибка обновления Google Sheets: {e}")

    def get_order_info(self, order_id):
        """Получение информации о заказе"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, user_name, phone, address, total_amount, status, payment_status, created_at
            FROM orders WHERE id = ?
        ''', (order_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'user_id': result[0],
                'user_name': result[1],
                'phone': result[2],
                'address': result[3],
                'total_amount': result[4],
                'status': result[5],
                'payment_status': result[6],
                'created_at': result[7]
            }
        return None

    def get_order_items(self, order_id):
        """Получение товаров заказа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.name, oi.quantity, oi.price
            FROM order_items oi
            JOIN dishes d ON oi.dish_id = d.id
            WHERE oi.order_id = ?
        ''', (order_id,))
        items = cursor.fetchall()
        conn.close()
        
        return [{'name': item[0], 'quantity': item[1], 'price': item[2]} for item in items]

    def get_order_total(self, order_id):
        """Получение суммы заказа"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT total_amount FROM orders WHERE id = ?', (order_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0

    # ... (остальные методы из предыдущей реализации: show_menu, show_category_dishes, show_dish_details, 
    # handle_quantity_change, add_to_cart, view_cart, checkout, handle_checkout_input, finalize_order, etc.)

    def setup_handlers(self, application):
        """Настройка обработчиков"""
        # Основные команды
        application.add_handler(CommandHandler("start", self.start))
        
        # Обработчики callback запросов
        application.add_handler(CallbackQueryHandler(self.show_menu, pattern="^menu$"))
        application.add_handler(CallbackQueryHandler(self.show_category_dishes, pattern="^category_"))
        application.add_handler(CallbackQueryHandler(self.show_dish_details, pattern="^dish_"))
        application.add_handler(CallbackQueryHandler(self.handle_quantity_change, pattern="^(increase|decrease)$"))
        application.add_handler(CallbackQueryHandler(self.add_to_cart, pattern="^add_to_cart$"))
        application.add_handler(CallbackQueryHandler(self.view_cart, pattern="^view_cart$"))
        application.add_handler(CallbackQueryHandler(self.checkout, pattern="^checkout$"))
        application.add_handler(CallbackQueryHandler(self.clear_cart, pattern="^clear_cart$"))
        application.add_handler(CallbackQueryHandler(self.show_admin_panel, pattern="^admin_panel$"))
        application.add_handler(CallbackQueryHandler(self.admin_change_payment, pattern="^admin_change_payment$"))
        application.add_handler(CallbackQueryHandler(self.back_to_main, pattern="^back_to_main$"))
        application.add_handler(CallbackQueryHandler(self.show_contacts, pattern="^contacts$"))
        application.add_handler(CallbackQueryHandler(self.voice_order, pattern="^voice_order$"))
        application.add_handler(CallbackQueryHandler(self.confirm_payment, pattern="^confirm_payment_"))
        
        # Обработчики сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_checkout_input))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_admin_input))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo_address))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_payment_screenshot))
        application.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    bot = FoodBot()
    bot.setup_handlers(application)
    
    print("🍖 Бот ФУД запущен с голосовыми командами и Google Sheets!")
    application.run_polling()

if __name__ == "__main__":
    main()