import os
import logging
import telegram.error
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

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
        'clear_cart': "🗑️ Очистить корзину",
        'checkout_order': "💳 Оформить заказ",
        'order_summary': "📋 Ваш заказ:",
        'delivery_info': "🚚 Доставка: 30-45 минут",
        'confirm_order': "✅ Подтвердить заказ",
        'choose_quantity': "Выберите количество:"
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
        'clear_cart': "🗑️ 장바구니 비우기",
        'checkout_order': "💳 주문하기",
        'order_summary': "📋 주문 내용:",
        'delivery_info': "🚚 배달: 30-45분",
        'confirm_order': "✅ 주문 확인",
        'choose_quantity': "수량을 선택하세요:"
    }
}


def get_translation(language, key):
    return TRANSLATIONS.get(language, TRANSLATIONS['ru']).get(key, key)

class FoodBot:
    def __init__(self):
        # Встроенные данные вместо базы данных
        self.categories = [
            {'id': 1, 'name_ru': '🍲 Первые блюда', 'name_ko': '🍲 첫 번째 요리'},
            {'id': 2, 'name_ru': '🍖 Вторые блюда', 'name_ko': '🍖 두 번째 요리'},
            {'id': 3, 'name_ru': '🥩 Стейки', 'name_ko': '🥩 스테이크'}
        ]
        
        self.dishes = [
            # Первые блюда
            {'id': 1, 'category_id': 1, 'name_ru': 'Борщ', 'name_ko': '보르시', 'price': 8000, 'weight': '400г', 
             'image_url': 'https://img.freepik.com/free-photo/traditional-russian-borscht_140725-300.jpg'},

            {'id': 2, 'category_id': 1, 'name_ru': 'Солянка', 'name_ko': '솔랸카', 'price': 8000, 'weight': '350г', 
             'image_url': 'https://img.freepik.com/free-photo/russian-solyanka-soup_140725-299.jpg'},
            
            {'id': 3, 'category_id': 1, 'name_ru': 'Шурпа', 'name_ko': '슈르파', 'price': 8000, 'weight': '450г',
             'image_url': 'https://img.freepik.com/free-photo/asian-shurpa-soup_140725-301.jpg'},

            {'id': 4, 'category_id': 1, 'name_ru': 'Мастава', 'name_ko': '마스타바', 'price': 8000, 'weight': '400г'},
            {'id': 5, 'category_id': 1, 'name_ru': 'Харчо', 'name_ko': '카르초', 'price': 8000, 'weight': '350г'},
            {'id': 6, 'category_id': 1, 'name_ru': 'Основа для лагмана', 'name_ko': '라그먼의 기초', 'price': 8000, 'weight': '450г'},
           
            # Вторые блюда
            {'id': 7, 'category_id': 2, 'name_ru': 'Тушенка говяжья', 'name_ko': '소고기 스튜', 'price': 10000, 'weight': '300г', 
             'image_url': 'https://img.freepik.com/free-photo/beef-stew-with-vegetables_140725-302.jpg'},
            
            {'id': 8, 'category_id': 2, 'name_ru': 'Тушенка свинная', 'name_ko': '돼지고기 조림', 'price': 10000, 'weight': '300г'},
            {'id': 9, 'category_id': 2, 'name_ru': 'Гуляш', 'name_ko': '굴라시', 'price': 8000, 'weight': '350г', 
             'image_url': 'https://img.freepik.com/free-photo/hungarian-goulash_140725-303.jpg'},

            {'id': 10, 'category_id': 2, 'name_ru': 'Мясо с грибами', 'name_ko': '버섯을 곁들인 고기', 'price': 9000, 'weight': '350г'},
            {'id': 11, 'category_id': 2, 'name_ru': 'Мясо с картошкой', 'name_ko': '고기와 감자', 'price': 9000, 'weight': '320г'},
            {'id': 12, 'category_id': 2, 'name_ru': 'Бефстроганов', 'name_ko': '비프 스트로가노프', 'price': 8000, 'weight': '320г', 
             'image_url': 'https://img.freepik.com/free-photo/beef-stroganoff-with-mushrooms_140725-304.jpg'},

            {'id': 13, 'category_id': 2, 'name_ru': 'Основа для  Беша', 'name_ko': '베샤의 기초', 'price': 7000, 'weight': '320г'},
            
            # Стейки
            {'id': 14, 'category_id': 3, 'name_ru': 'Томогавк', 'name_ko': '토마호크', 'price': 12000, 'weight': '500г', 
              'image_url': 'https://img.freepik.com/free-photo/tomahawk-steak_140725-305.jpg'},

            {'id': 15, 'category_id': 3, 'name_ru': 'Рибай', 'name_ko': '립아이', 'price': 9500, 'weight': '400г', 
             'image_url': 'https://img.freepik.com/free-photo/ribeye-steak_140725-306.jpg'},

            {'id': 16, 'category_id': 3, 'name_ru': 'Нью-Йорк', 'name_ko': '뉴욕 스테이크', 'price': 8500, 'weight': '350г', 
             'image_url': 'https://img.freepik.com/free-photo/new-york-strip-steak_140725-307.jpg'},

            {'id': 17, 'category_id': 3, 'name_ru': 'Т-бон', 'name_ko': '티본', 'price': 8500, 'weight': '350г'}
        ]
        
        # Хранилище в памяти
        self.user_data_store = {}
        logging.info("✅ Бот инициализирован")

    def get_user_language(self, user_id):
        """Получить язык пользователя - с принудительным русским по умолчанию"""
        user_data = self.user_data_store.get(user_id, {})
        language = user_data.get('language', 'ru')
    
        # Принудительно устанавливаем русский если язык не распознан
        if language not in ['ru', 'ko']:
            language = 'ru'
            self.set_user_language(user_id, language)
        
        return language
    
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
            button_text = f"{name} - {dish['price']}won"
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
        """Показать информацию о блюде с количеством - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
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
        
        dish_text = f"🍽️ {name}\n"
        dish_text += f"💰 {get_translation(language, 'price')} {dish['price']}₽\n"
        if dish['weight']:
            dish_text += f"⚖️ {dish['weight']}\n"
        
        # Сохраняем ВСЮ информацию о блюде
        context.user_data['selected_dish'] = {
            'id': dish['id'],
            'name_ru': dish['name_ru'],
            'name_ko': dish['name_ko'], 
            'price': dish['price'],
            'category_id': dish['category_id'],
            'image_url': dish.get('image_url', '')
        }
        context.user_data['quantity'] = 1  # Сбрасываем количество
        
        # Клавиатура для выбора количества
        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data="decrease"),
                InlineKeyboardButton("1", callback_data="quantity_display"),
                InlineKeyboardButton("➕", callback_data="increase")
            ],
            [InlineKeyboardButton(get_translation(language, 'add_to_cart'), callback_data="add_to_cart")],
            [InlineKeyboardButton(get_translation(language, 'back'), callback_data=f"cat_{dish['category_id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        dish_text += f"\n{get_translation(language, 'choose_quantity')}"
        
        # Пытаемся отправить с изображением
        if dish.get('image_url'):
            try:
                await query.message.reply_photo(
                    photo=dish['image_url'],
                    caption=dish_text,
                    reply_markup=reply_markup
                )
                await query.delete_message()
                return
            except Exception as e:
                logging.error(f"Ошибка загрузки изображения: {e}")
        
        # Если изображение не загрузилось, отправляем текст
        await query.edit_message_text(
            dish_text,
            reply_markup=reply_markup
        )
    
    async def handle_quantity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Изменение количества - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        # Получаем текущее количество
        current_quantity = context.user_data.get('quantity', 1)
        
        # Определяем действие
        if query.data == "increase":
            new_quantity = current_quantity + 1
        elif query.data == "decrease" and current_quantity > 1:
            new_quantity = current_quantity - 1
        else:
            new_quantity = current_quantity
        
        # Сохраняем новое количество
        context.user_data['quantity'] = new_quantity
        
        # Получаем данные о блюде
        dish_data = context.user_data.get('selected_dish')
        if not dish_data:
            await query.edit_message_text("❌ Ошибка: блюдо не найдено")
            return
        
        name = dish_data['name_ko'] if language == 'ko' else dish_data['name_ru']
        
        # Создаем клавиатуру с новым количеством
        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data="decrease"),
                InlineKeyboardButton(str(new_quantity), callback_data="quantity_display"),
                InlineKeyboardButton("➕", callback_data="increase")
            ],
            [InlineKeyboardButton(get_translation(language, 'add_to_cart'), callback_data="add_to_cart")],
            [InlineKeyboardButton(get_translation(language, 'back'), callback_data=f"cat_{dish_data['category_id']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Текст сообщения
        dish_text = f"🍽️ {name}\n💰 {get_translation(language, 'price')} {dish_data['price']}₽\n\n{get_translation(language, 'choose_quantity')}"
        
        # Обновляем сообщение
        try:
            await query.edit_message_text(
                dish_text,
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Ошибка обновления сообщения: {e}")
    
    async def handle_quantity_display(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просто показывает текущее количество (не меняет его)"""
        query = update.callback_query
        await query.answer()  # Убираем "часики"

    async def handle_add_to_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавить в корзину - с отладкой"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        # ОТЛАДКА: проверяем что в контексте
        logging.info(f"🔄 Добавление в корзину. Язык: {language}")
        logging.info(f"📦 Данные в контексте: {context.user_data.keys()}")
        
        # Получаем данные о выбранном блюде
        dish_data = context.user_data.get('selected_dish')
        if not dish_data:
            await query.edit_message_text("❌ Ошибка: блюдо не выбрано")
            return
        
        quantity = context.user_data.get('quantity', 1)
        
        # ОТЛАДКА: информация о блюде
        logging.info(f"🍽️ Добавляемое блюдо: {dish_data['name_ru']}, количество: {quantity}")
        
        # Получаем текущую корзину
        cart = self.get_user_cart(user_id)
        
        dish_key = str(dish_data['id'])
        name = dish_data['name_ko'] if language == 'ko' else dish_data['name_ru']
        
        # Добавляем в корзину
        if dish_key in cart:
            cart[dish_key]['quantity'] += quantity
        else:
            cart[dish_key] = {
                'name': name,
                'price': dish_data['price'],
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
            cart_text += f"• {item_data['name']} x{item_data['quantity']} - {item_total}won\n"
        
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
    
    async def handle_checkout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать оформление заказа"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        cart = self.get_user_cart(user_id)
        
        if not cart:
            await query.edit_message_text(get_translation(language, 'cart_empty'))
            return
        
        # Начинаем процесс оформления
        context.user_data['checkout_step'] = 'name'
        
        await query.edit_message_text(get_translation(language, 'checkout_name'))

    async def handle_checkout_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ввода данных для заказа"""
        user_id = update.effective_user.id
        text = update.message.text
        language = self.get_user_language(user_id)
        step = context.user_data.get('checkout_step')
        
        if step == 'name':
            context.user_data['order_name'] = text
            context.user_data['checkout_step'] = 'phone'
            await update.message.reply_text(get_translation(language, 'checkout_phone'))
        
        elif step == 'phone':
            context.user_data['order_phone'] = text
            context.user_data['checkout_step'] = 'address'
            await update.message.reply_text(get_translation(language, 'checkout_address'))
        
        elif step == 'address':
            context.user_data['order_address'] = text
            await self.finalize_order(update, context)

    async def finalize_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Завершение оформления заказа"""
        user_id = update.effective_user.id
        language = self.get_user_language(user_id)
        cart = self.get_user_cart(user_id)
        
        if not cart:
            await update.message.reply_text(get_translation(language, 'cart_empty'))
            return
        
        # Рассчитываем итоговую сумму
        total = sum(item['price'] * item['quantity'] for item in cart.values())
        
        # Сохраняем заказ
        order_id = self.save_order(user_id, {
            'name': context.user_data['order_name'],
            'phone': context.user_data['order_phone'],
            'address': context.user_data['order_address'],
            'total': total,
            'items': cart
        })
        
        # Показываем реквизиты для оплаты
        payment_text = (
            f"{get_translation(language, 'payment_details')}"
            f"{get_translation(language, 'payment_amount')} {total}won\n\n"
            f"{get_translation(language, 'bank_details')}"
            f"{get_translation(language, 'send_screenshot')}"
        )
        
        # Сохраняем информацию о заказе
        context.user_data['current_order_id'] = order_id
        context.user_data['waiting_payment'] = True
        
        keyboard = [
            [InlineKeyboardButton("📸 Отправить скриншот оплаты", callback_data="send_screenshot")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            payment_text,
            reply_markup=reply_markup
        )
        
        # Уведомляем администратора
        await self.notify_admin_about_order(context.bot, order_id, user_id)
        
        # Очищаем корзину
        self.set_user_cart(user_id, {})
        context.user_data['checkout_step'] = None

    def save_order(self, user_id, order_data):
        """Сохранить заказ (в реальном проекте - в базу данных)"""
        # Генерируем ID заказа
        order_id = f"ORDER_{user_id}_{len(self.user_data_store) + 1}"
        
        # Сохраняем заказ
        if 'orders' not in self.user_data_store:
            self.user_data_store['orders'] = {}
        self.user_data_store['orders'][order_id] = {
            'user_id': user_id,
            'status': 'waiting_payment',
            'created_at': 'datetime',  # В реальном проекте использовать datetime
            **order_data
        }
        
        return order_id

    async def notify_admin_about_order(self, bot, order_id, user_id):
        """Уведомить администратора о новом заказе"""
        # ID администратора (замените на реальный)
        ADMIN_ID = os.getenv('ADMIN_ID', '379494671')
        
        order = self.user_data_store['orders'].get(order_id)
        if not order:
            return
        
        order_text = (
            f"🆕 НОВЫЙ ЗАКАЗ #{order_id}\n\n"
            f"👤 Клиент: {order['name']}\n"
            f"📞 Телефон: {order['phone']}\n"
            f"🏠 Адрес: {order['address']}\n"
            f"💰 Сумма: {order['total']}won\n\n"
            f"📦 Состав заказа:\n"
        )
        
        for item_id, item in order['items'].items():
            order_text += f"• {item['name']} x{item['quantity']} - {item['price'] * item['quantity']}₽\n"
        
        try:
            await bot.send_message(ADMIN_ID, order_text)
        except Exception as e:
            logging.error(f"Ошибка уведомления админа: {e}")

        # Добавьте обработчик для скриншотов
    async def handle_payment_screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка скриншота оплаты"""
        user_id = update.effective_user.id
        language = self.get_user_language(user_id)
        
        if not context.user_data.get('waiting_payment'):
            return
        
        # Получаем фото
        photo = update.message.photo[-1] if update.message.photo else None
        
        if photo:
            # В реальном проекте сохраняем файл
            # file = await photo.get_file()
            # await file.download_to_drive(f"payments/{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            
            order_id = context.user_data.get('current_order_id')
            
            # Обновляем статус заказа
            if order_id and order_id in self.user_data_store.get('orders', {}):
                self.user_data_store['orders'][order_id]['status'] = 'payment_received'
            
            # Уведомляем пользователя
            await update.message.reply_text(
                get_translation(language, 'payment_received')
            )
            
            # Уведомляем администратора
            await self.notify_admin_about_payment(context.bot, order_id, user_id)
            
            context.user_data['waiting_payment'] = False
            
            # Показываем главное меню
            await self.show_main_menu_after_payment(update, context, language)

    async def notify_admin_about_payment(self, bot, order_id, user_id):
        """Уведомить администратора об оплате"""
        ADMIN_ID = os.getenv('ADMIN_ID', '379494671')
        
        order = self.user_data_store['orders'].get(order_id)
        if not order:
            return
        
        payment_text = (
            f"✅ ОПЛАЧЕНО #{order_id}\n\n"
            f"👤 Клиент: {order['name']}\n"
            f"📞 Телефон: {order['phone']}\n"
            f"💰 Сумма: {order['total']}won\n\n"
            f"📍 Можно готовить и доставлять!"
        )
        
        try:
            await bot.send_message(ADMIN_ID, payment_text)
        except Exception as e:
            logging.error(f"Ошибка уведомления админа об оплате: {e}")

    async def show_main_menu_after_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language):
        """Показать главное меню после оплаты"""
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
        
        if update.message:
            await update.message.reply_text(
                get_translation(language, 'welcome'),
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
🏠 Адрес: Ansan
⏰ Время работы: 9:00 - 21:00

Доставка по всему городу!""",
            
            'ko': """📞 푸드 컴퍼니 연락처:

📞 전화: +82 10-8361-6165
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
    
    # В методе setup_handlers добавьте новые обработчики:
    def setup_handlers(self, application):
        """Настройка обработчиков"""
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.handle_language, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.handle_menu, pattern="^menu$"))
        application.add_handler(CallbackQueryHandler(self.handle_category, pattern="^cat_"))
        application.add_handler(CallbackQueryHandler(self.handle_dish, pattern="^dish_"))
        application.add_handler(CallbackQueryHandler(self.handle_quantity, pattern="^(increase|decrease)$"))
        application.add_handler(CallbackQueryHandler(self.handle_quantity_display, pattern="^quantity_display$"))
        application.add_handler(CallbackQueryHandler(self.handle_add_to_cart, pattern="^add_to_cart$"))
        application.add_handler(CallbackQueryHandler(self.handle_cart, pattern="^cart$"))
        application.add_handler(CallbackQueryHandler(self.handle_clear_cart, pattern="^clear_cart$"))
        application.add_handler(CallbackQueryHandler(self.handle_contacts, pattern="^contacts$"))
        application.add_handler(CallbackQueryHandler(self.handle_back, pattern="^back$"))
        application.add_handler(CallbackQueryHandler(self.handle_checkout, pattern="^checkout$"))
        application.add_handler(CallbackQueryHandler(self.handle_confirm_checkout, pattern="^confirm_checkout$"))
        
        # Обработчики сообщений
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_checkout_input))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_payment_screenshot))

import asyncio
import time

def main():
    """Основная функция с обработкой конфликтов"""
    token = os.getenv('BOT_TOKEN')
    if not token:
        logging.error("❌ BOT_TOKEN не найден в переменных окружения")
        return
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Создаем application
            application = Application.builder().token(token).build()
            
            # Инициализируем бота
            bot = FoodBot()
            bot.setup_handlers(application)
            
            # Запускаем бота
            logging.info(f"🚀 Попытка запуска бота #{retry_count + 1}...")
            application.run_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES,
                poll_interval=1.0,  # Интервал опроса
                timeout=10  # Таймаут запроса
            )
            break  # Если успешно, выходим из цикла
            
        except telegram.error.Conflict as e:
            retry_count += 1
            logging.error(f"❌ Конфликт (попытка {retry_count}/{max_retries}): {e}")
            
            if retry_count < max_retries:
                logging.info("🔄 Перезапуск через 10 секунд...")
                time.sleep(10)
            else:
                logging.error("❌ Превышено количество попыток перезапуска")
                break
                
        except Exception as e:
            logging.error(f"❌ Другая ошибка: {e}")
            break

if __name__ == "__main__":
    main()