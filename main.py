import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio

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
        # Вместо базы данных используем встроенные данные
        self.categories = [
            {'id': 1, 'name_ru': '🍲 Первые блюда', 'name_ko': '🍲 첫 번째 요리'},
            {'id': 2, 'name_ru': '🍖 Вторые блюда', 'name_ko': '🍖 두 번째 요리'},
            {'id': 3, 'name_ru': '🥩 Стейки', 'name_ko': '🥩 스테이크'}
        ]
        
        self.dishes = [
            # Первые блюда
            {'id': 1, 'category_id': 1, 'name_ru': 'Борщ', 'name_ko': '보르시', 
             'description_ru': 'Ароматный борщ со сметаной', 'description_ko': '사워 크림이 있는 향기로운 보르시',
             'price': 250, 'weight': '400г'},
            {'id': 2, 'category_id': 1, 'name_ru': 'Солянка', 'name_ko': '솔랸카',
             'description_ru': 'Наваристая солянка', 'description_ko': '풍미로운 솔랸카',
             'price': 280, 'weight': '350г'},
            {'id': 3, 'category_id': 1, 'name_ru': 'Шурпа', 'name_ko': '슈르파',
             'description_ru': 'Ароматная шурпа', 'description_ko': '향기로운 슈르파',
             'price': 300, 'weight': '450г'},
            
            # Вторые блюда
            {'id': 4, 'category_id': 2, 'name_ru': 'Тушенка говяжья', 'name_ko': '소고기 스튜',
             'description_ru': 'Нежная тушеная говядина', 'description_ko': '부드러운 소고기 스튜',
             'price': 350, 'weight': '300г'},
            {'id': 5, 'category_id': 2, 'name_ru': 'Гуляш', 'name_ko': '굴라시',
             'description_ru': 'Венгерский гуляш', 'description_ko': '헝가리식 굴라시',
             'price': 320, 'weight': '350г'},
            {'id': 6, 'category_id': 2, 'name_ru': 'Бефстроганов', 'name_ko': '비프 스트로가노프',
             'description_ru': 'Нежное мясо в сметанном соусе', 'description_ko': '사워 크림 소스가 있는 부드러운 고기',
             'price': 380, 'weight': '320г'},
            
            # Стейки
            {'id': 7, 'category_id': 3, 'name_ru': 'Томогавк', 'name_ko': '토마호크',
             'description_ru': 'Сочный стейк томагавк', 'description_ko': '육즙이 많은 토마호크 스테이크',
             'price': 1200, 'weight': '500г'},
            {'id': 8, 'category_id': 3, 'name_ru': 'Рибай', 'name_ko': '립아이',
             'description_ru': 'Нежный рибай стейк', 'description_ko': '부드러운 립아이 스테이크',
             'price': 950, 'weight': '400г'},
            {'id': 9, 'category_id': 3, 'name_ru': 'Нью-Йорк', 'name_ko': '뉴욕 스테이크',
             'description_ru': 'Классический Нью-Йорк стейк', 'description_ko': '클래식 뉴욕 스테이크',
             'price': 850, 'weight': '350г'}
        ]
        
        # Хранилище для пользователей и корзин в памяти
        self.user_data_store = {}
        logging.info("✅ Бот инициализирован (без базы данных)")
    
    def get_user_language(self, user_id):
        """Получить язык пользователя"""
        user_data = self.user_data_store.get(user_id, {})
        return user_data.get('language', 'ru')
    
    def set_user_language(self, user_id, language):
        """Установить язык пользователя"""
        if user_id not in self.user_data_store:
            self.user_data_store[user_id] = {}
        self.user_data_store[user_id]['language'] = language
    
    def get_user_cart(self, user_id):
        """Получить корзину пользователя"""
        user_data = self.user_data_store.get(user_id, {})
        return user_data.get('cart', {})
    
    def set_user_cart(self, user_id, cart):
        """Установить корзину пользователя"""
        if user_id not in self.user_data_store:
            self.user_data_store[user_id] = {}
        self.user_data_store[user_id]['cart'] = cart
    
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
        
        keyboard = []
        for category in self.categories:
            name = category['name_ko'] if language == 'ko' else category['name_ru']
            keyboard.append([InlineKeyboardButton(name, callback_data=f"cat_{category['id']}")])
        
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
        
        category_dishes = [d for d in self.dishes if d['category_id'] == category_id]
        
        if not category_dishes:
            keyboard = [[InlineKeyboardButton(get_translation(language, 'back'), callback_data="menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                get_translation(language, 'cart_empty'),
                reply_markup=reply_markup
            )
            return
        
        keyboard = []
        for dish in category_dishes:
            name = dish['name_ko'] if language == 'ko' else dish['name_ru']
            button_text = f"{name} - {dish['price']}₽"
            if dish['weight']:
                button_text += f" ({dish['weight']})"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"dish_{dish['id']}")])
        
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
        
        dish = next((d for d in self.dishes if d['id'] == dish_id), None)
        
        if not dish:
            await query.edit_message_text("Блюдо не найдено")
            return
        
        name = dish['name_ko'] if language == 'ko' else dish['name_ru']
        description = dish['description_ko'] if language == 'ko' else dish['description_ru']
        
        dish_text = f"🍽️ {name}\n"
        dish_text += f"💰 {get_translation(language, 'price')} {dish['price']}₽\n"
        if dish['weight']:
            dish_text += f"⚖️ {dish['weight']}\n"
        if description:
            dish_text += f"📝 {description}\n"
        
        # Сохраняем выбранное блюдо
        context.user_data['selected_dish'] = dish
        context.user_data['quantity'] = 1
        
        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data="decrease"),
                InlineKeyboardButton("1", callback_data="quantity_1"),
                InlineKeyboardButton("➕", callback_data="increase")
            ],
            [InlineKeyboardButton(get_translation(language, 'add_to_cart'), callback_data="add_to_cart")],
            [InlineKeyboardButton(get_translation(language, 'back'), callback_data=f"cat_{dish['category_id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            dish_text + f"\n{get_translation(language, 'choose_category')}",
            reply_markup=reply_markup
        )
    
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
        name = dish['name_ko'] if language == 'ko' else dish['name_ru']
        
        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data="decrease"),
                InlineKeyboardButton(str(new_quantity), callback_data=f"quantity_{new_quantity}"),
                InlineKeyboardButton("➕", callback_data="increase")
            ],
            [InlineKeyboardButton(get_translation(language, 'add_to_cart'), callback_data="add_to_cart")],
            [InlineKeyboardButton(get_translation(language, 'back'), callback_data=f"cat_{dish['category_id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        dish_text = f"🍽️ {name}\n💰 {get_translation(language, 'price')} {dish['price']}₽\n\n{get_translation(language, 'choose_category')}"
        
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
        
        # Получаем текущую корзину
        cart = self.get_user_cart(user_id)
        
        dish_key = str(dish['id'])
        name = dish['name_ko'] if language == 'ko' else dish['name_ru']
        
        if dish_key in cart:
            cart[dish_key]['quantity'] += quantity
        else:
            cart[dish_key] = {
                'name': name,
                'price': dish['price'],
                'quantity': quantity
            }
        
        # Сохраняем корзину
        self.set_user_cart(user_id, cart)
        
        keyboard = [
            [InlineKeyboardButton("🛒 " + get_translation(language, 'cart'), callback_data="cart")],
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ {name} x{quantity} {get_translation(language, 'add_to_cart')}!",
            reply_markup=reply_markup
        )
    
    async def handle_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать корзину"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        cart = self.get_user_cart(user_id)
        
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
        
        self.set_user_cart(user_id, {})
        
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

📞 Телефон: +7 (999) 123-45-67
📧 Email: info@food-company.ru
🏠 Адрес: г. Москва, ул. Примерная, д. 1
⏰ Время работы: 9:00 - 21:00

Доставка по всему городу!""",
            
            'ko': """📞 푸드 컴퍼니 연락처:

📞 전화: +7 (999) 123-45-67
📧 이메일: info@food-company.ru
🏠 주소: 모스크바, 프리메르나야 거리 1
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

def main():
    """Основная функция"""
    token = os.getenv('BOT_TOKEN')
    if not token:
        logging.error("❌ BOT_TOKEN не найден в переменных окружения")
        return
    
    try:
        # Создаем application
        application = Application.builder().token(token).build()
        
        # Инициализируем бота
        bot = FoodBot()
        bot.setup_handlers(application)
        
        # Запускаем бота
        logging.info("🚀 Бот запускается...")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        logging.error(f"❌ Ошибка запуска бота: {e}")
    finally:
        logging.info("🛑 Бот остановлен")

if __name__ == "__main__":
    main()