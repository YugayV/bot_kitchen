import os
import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Переводы
TRANSLATIONS = {
    'ru': {
        'welcome': "🍖 Добро пожаловать в ФУД!",
        'menu': "📋 Меню",
        'cart': "🛒 Корзина", 
        'contacts': "📞 Контакты",
        'back': "🔙 Назад",
        'choose_category': "Выберите категорию:",
        'language_changed': "🌐 Язык изменен на русский",
        'choose_language': "Выберите язык:",
        'add_to_cart': "🛒 Добавить в корзину",
        'price': "Цена:",
        'cart_empty': "🛒 Корзина пуста",
        'cart_items': "🛒 Ваша корзина:",
        'total': "💰 Итого:",
        'checkout': "💳 Оформить заказ",
        'clear_cart': "🗑️ Очистить корзину"
    },
    'ko': {
        'welcome': "🍖 푸드 컴퍼니에 오신 것을 환영합니다!",
        'menu': "📋 메뉴", 
        'cart': "🛒 장바구니",
        'contacts': "📞 연락처",
        'back': "🔙 뒤로",
        'choose_category': "카테고리를 선택하세요:",
        'language_changed': "🌐 언어가 한국어로 변경되었습니다",
        'choose_language': "언어 선택:",
        'add_to_cart': "🛒 장바구니에 추가",
        'price': "가격:",
        'cart_empty': "🛒 장바구니가 비어 있습니다",
        'cart_items': "🛒 장바구니:",
        'total': "💰 총액:",
        'checkout': "💳 주문하기",
        'clear_cart': "🗑️ 장바구니 비우기"
    }
}

def get_translation(language, key):
    return TRANSLATIONS.get(language, TRANSLATIONS['ru']).get(key, key)

class FoodBot:
    def __init__(self):
        self.db_path = 'food_bot.db'
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'ru',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица категорий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name_ru TEXT,
                name_ko TEXT,
                display_order INTEGER
            )
        ''')
        
        # Таблица блюд
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dishes (
                id INTEGER PRIMARY KEY,
                category_id INTEGER,
                name_ru TEXT,
                name_ko TEXT,
                description_ru TEXT,
                description_ko TEXT,
                price INTEGER,
                weight TEXT,
                image_path TEXT
            )
        ''')
        
        # Проверяем есть ли данные
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            # Добавляем категории
            categories = [
                (1, '🍲 Первые блюда', '🍲 첫 번째 요리', 1),
                (2, '🍖 Вторые блюда', '🍖 두 번째 요리', 2),
                (3, '🥩 Стейки', '🥩 스테이크', 3)
            ]
            cursor.executemany(
                "INSERT INTO categories (id, name_ru, name_ko, display_order) VALUES (?, ?, ?, ?)", 
                categories
            )
            
            # Добавляем блюда
            dishes = [
                # Первые блюда
                (1, 1, 'Борщ', '보르시', 
                 'Ароматный борщ со сметаной', '사워 크림이 있는 향기로운 보르시', 
                 250, '400г', ''),
                (2, 1, 'Солянка', '솔랸카',
                 'Наваристая солянка', '풍미로운 솔랸카',
                 280, '350г', ''),
                (3, 1, 'Шурпа', '슈르파',
                 'Ароматная шурпа', '향기로운 슈르파',
                 300, '450г', ''),
                
                # Вторые блюда
                (4, 2, 'Тушенка говяжья', '소고기 스튜',
                 'Нежная тушеная говядина', '부드러운 소고기 스튜',
                 350, '300г', ''),
                (5, 2, 'Гуляш', '굴라시',
                 'Венгерский гуляш', '헝가리식 굴라시',
                 320, '350г', ''),
                (6, 2, 'Бефстроганов', '비프 스트로가노프',
                 'Нежное мясо в сметанном соусе', '사워 크림 소스가 있는 부드러운 고기',
                 380, '320г', ''),
                
                # Стейки
                (7, 3, 'Томогавк', '토마호크',
                 'Сочный стейк томагавк', '육즙이 많은 토마호크 스테이크',
                 1200, '500г', ''),
                (8, 3, 'Рибай', '립아이',
                 'Нежный рибай стейк', '부드러운 립아이 스테이크',
                 950, '400г', ''),
                (9, 3, 'Нью-Йорк', '뉴욕 스테이크',
                 'Классический Нью-Йорк стейк', '클래식 뉴욕 스테이크',
                 850, '350г', '')
            ]
            
            cursor.executemany('''
                INSERT INTO dishes (id, category_id, name_ru, name_ko, 
                description_ru, description_ko, price, weight, image_path) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', dishes)
        
        conn.commit()
        conn.close()
        logging.info("✅ База данных инициализирована")
    
    def get_user_language(self, user_id):
        """Получить язык пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 'ru'
    
    def set_user_language(self, user_id, language):
        """Установить язык пользователя"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)
        ''', (user_id, language))
        conn.commit()
        conn.close()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        language = self.get_user_language(user_id)
        
        keyboard = [
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
            [InlineKeyboardButton("🛒 " + get_translation(language, 'cart'), callback_data="cart")],
            [
                InlineKeyboardButton("🇰🇷 한국어", callback_data="lang_ko"),
                InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
            ],
            [InlineKeyboardButton("📞 " + get_translation(language, 'contacts'), callback_data="contacts")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            get_translation(language, 'welcome') + "\n\n" + get_translation(language, 'choose_language'),
            reply_markup=reply_markup
        )
    
    async def handle_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Смена языка"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = query.data.split('_')[1]
        
        self.set_user_language(user_id, language)
        await self.show_main_menu(query, language)
    
    async def show_main_menu(self, query, language):
        """Показать главное меню"""
        keyboard = [
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
            [InlineKeyboardButton("🛒 " + get_translation(language, 'cart'), callback_data="cart")],
            [
                InlineKeyboardButton("🇰🇷 한국어", callback_data="lang_ko"),
                InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
            ],
            [InlineKeyboardButton("📞 " + get_translation(language, 'contacts'), callback_data="contacts")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_translation(language, 'welcome'),
            reply_markup=reply_markup
        )
    
    async def handle_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать меню"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name_ru, name_ko FROM categories ORDER BY display_order")
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
    
    async def handle_category(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать блюда категории"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        category_id = int(query.data.split('_')[1])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name_ru, name_ko, price, weight 
            FROM dishes WHERE category_id = ? ORDER BY id
        ''', (category_id,))
        dishes = cursor.fetchall()
        conn.close()
        
        if not dishes:
            keyboard = [[InlineKeyboardButton(get_translation(language, 'back'), callback_data="menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                get_translation(language, 'cart_empty'),
                reply_markup=reply_markup
            )
            return
        
        keyboard = []
        for dish_id, name_ru, name_ko, price, weight in dishes:
            name = name_ko if language == 'ko' else name_ru
            button_text = f"{name} - {price}₽"
            if weight:
                button_text += f" ({weight})"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"dish_{dish_id}")])
        
        keyboard.append([InlineKeyboardButton(get_translation(language, 'back'), callback_data="menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_translation(language, 'choose_category'),
            reply_markup=reply_markup
        )
    
    async def handle_dish(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать информацию о блюде"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        dish_id = int(query.data.split('_')[1])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT name_ru, name_ko, description_ru, description_ko, price, weight 
            FROM dishes WHERE id = ?
        ''', (dish_id,))
        dish = cursor.fetchone()
        conn.close()
        
        if not dish:
            await query.edit_message_text("Блюдо не найдено")
            return
        
        name_ru, name_ko, desc_ru, desc_ko, price, weight = dish
        name = name_ko if language == 'ko' else name_ru
        description = desc_ko if language == 'ko' else desc_ru
        
        dish_text = f"🍽️ {name}\n"
        dish_text += f"💰 {get_translation(language, 'price')} {price}₽\n"
        if weight:
            dish_text += f"⚖️ {weight}\n"
        if description:
            dish_text += f"📝 {description}\n"
        
        # Сохраняем выбранное блюдо
        context.user_data['selected_dish'] = {
            'id': dish_id,
            'name': name,
            'price': price
        }
        context.user_data['quantity'] = 1
        
        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data="decrease"),
                InlineKeyboardButton("1", callback_data="quantity_1"),
                InlineKeyboardButton("➕", callback_data="increase")
            ],
            [InlineKeyboardButton(get_translation(language, 'add_to_cart'), callback_data="add_to_cart")],
            [InlineKeyboardButton(get_translation(language, 'back'), callback_data=f"cat_{self.get_dish_category(dish_id)}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            dish_text + f"\n{get_translation(language, 'choose_category')}",
            reply_markup=reply_markup
        )
    
    def get_dish_category(self, dish_id):
        """Получить категорию блюда"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT category_id FROM dishes WHERE id = ?", (dish_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 1
    
    async def handle_quantity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Изменение количества"""
        query = update.callback_query
        await query.answer()
        
        action = query.data
        current_quantity = context.user_data.get('quantity', 1)
        
        if action == "increase":
            new_quantity = current_quantity + 1
        elif action == "decrease" and current_quantity > 1:
            new_quantity = current_quantity - 1
        else:
            new_quantity = current_quantity
        
        context.user_data['quantity'] = new_quantity
        
        dish = context.user_data['selected_dish']
        language = self.get_user_language(query.from_user.id)
        
        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data="decrease"),
                InlineKeyboardButton(str(new_quantity), callback_data=f"quantity_{new_quantity}"),
                InlineKeyboardButton("➕", callback_data="increase")
            ],
            [InlineKeyboardButton(get_translation(language, 'add_to_cart'), callback_data="add_to_cart")],
            [InlineKeyboardButton(get_translation(language, 'back'), callback_data=f"cat_{self.get_dish_category(dish['id'])}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        dish_text = f"🍽️ {dish['name']}\n💰 {get_translation(language, 'price')} {dish['price']}₽\n\n{get_translation(language, 'choose_category')}"
        
        await query.edit_message_text(
            dish_text,
            reply_markup=reply_markup
        )
    
    async def handle_add_to_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавить в корзину"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        dish = context.user_data['selected_dish']
        quantity = context.user_data.get('quantity', 1)
        
        # Инициализируем корзину
        if 'cart' not in context.user_data:
            context.user_data['cart'] = {}
        
        cart = context.user_data['cart']
        dish_key = str(dish['id'])
        
        if dish_key in cart:
            cart[dish_key]['quantity'] += quantity
        else:
            cart[dish_key] = {
                'name': dish['name'],
                'price': dish['price'],
                'quantity': quantity
            }
        
        keyboard = [
            [InlineKeyboardButton("🛒 " + get_translation(language, 'cart'), callback_data="cart")],
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ {dish['name']} x{quantity} {get_translation(language, 'add_to_cart')}!",
            reply_markup=reply_markup
        )
    
    async def handle_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать корзину"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        cart = context.user_data.get('cart', {})
        
        if not cart:
            keyboard = [[InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                get_translation(language, 'cart_empty'),
                reply_markup=reply_markup
            )
            return
        
        cart_text = get_translation(language, 'cart_items') + "\n\n"
        total = 0
        
        for item_id, item_data in cart.items():
            item_total = item_data['price'] * item_data['quantity']
            total += item_total
            cart_text += f"• {item_data['name']} x{item_data['quantity']} - {item_total}₽\n"
        
        cart_text += f"\n{get_translation(language, 'total')} {total}₽"
        
        keyboard = [
            [InlineKeyboardButton("💳 " + get_translation(language, 'checkout'), callback_data="checkout")],
            [InlineKeyboardButton("🗑️ " + get_translation(language, 'clear_cart'), callback_data="clear_cart")],
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            cart_text,
            reply_markup=reply_markup
        )
    
    async def handle_clear_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Очистить корзину"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        context.user_data['cart'] = {}
        
        keyboard = [[InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_translation(language, 'cart_empty'),
            reply_markup=reply_markup
        )
    
    async def handle_contacts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать контакты"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        contacts_text = {
            'ru': """📞 Контакты компании ФУД:

📞 Телефон: +82 10-8361-6165
📧 Email: vamp.09.94@gmail.com
🏠 Адрес: Ansan
⏰ Время работы: 9:00 - 21:00

Доставка по всему городу!""",
            
            'ko': """📞 푸드 컴퍼니 연락처:

📞 전화: +82 10-8361-6165
📧 이메일: vamp.09.94@gmail.com
🏠 주소: Ansan
⏰ 영업 시간: 9:00 - 21:00

도시 전체 배달 가능!"""
        }
        
        keyboard = [[InlineKeyboardButton(get_translation(language, 'back'), callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            contacts_text.get(language, contacts_text['ru']),
            reply_markup=reply_markup
        )
    
    async def handle_back(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Назад в главное меню"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        await self.show_main_menu(query, language)
    
    def setup_handlers(self, application):
        """Настройка обработчиков"""
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.handle_language, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.handle_menu, pattern="^menu$"))
        application.add_handler(CallbackQueryHandler(self.handle_category, pattern="^cat_"))
        application.add_handler(CallbackQueryHandler(self.handle_dish, pattern="^dish_"))
        application.add_handler(CallbackQueryHandler(self.handle_quantity, pattern="^(increase|decrease)$"))
        application.add_handler(CallbackQueryHandler(self.handle_add_to_cart, pattern="^add_to_cart$"))
        application.add_handler(CallbackQueryHandler(self.handle_cart, pattern="^cart$"))
        application.add_handler(CallbackQueryHandler(self.handle_clear_cart, pattern="^clear_cart$"))
        application.add_handler(CallbackQueryHandler(self.handle_contacts, pattern="^contacts$"))
        application.add_handler(CallbackQueryHandler(self.handle_back, pattern="^back$"))

async def main():
    """Основная функция"""
    token = os.getenv('BOT_TOKEN')
    if not token:
        logging.error("❌ BOT_TOKEN не найден в переменных окружения")
        return
    
    application = Application.builder().token(token).build()
    
    bot = FoodBot()
    bot.setup_handlers(application)
    
    logging.info("🚀 Бот запущен с поддержкой корейского языка!")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())