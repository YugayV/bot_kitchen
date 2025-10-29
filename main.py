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
        'welcome_message': """🌟 <b>Добро пожаловать в ФУД-бот!</b> 🌟

🍽️ Мы рады приветствовать вас в нашем уютном кулинарном мире! 

Здесь вы можете:
• 📋 Просмотреть наше разнообразное меню
• 🛒 Собрать любимые блюда в корзину
• 🚚 Оформить быструю доставку
• 💳 Оплатить заказ удобным способом

Выберите язык для продолжения:""",
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
        'choose_quantity': "Выберите количество:",
        'go_to_cart': "🛒 Перейти в корзину",
        'checkout_name': "📝 Введите ваше имя:",
        'checkout_phone': "📞 Введите ваш телефон:",
        'checkout_address': "🏠 Введите адрес доставки:",
        'payment_details': "💳 Реквизиты для оплаты:\n\n",
        'payment_amount': "Сумма к оплате:",
        'bank_details': "🏦 Банковские реквизиты:\nKB국민은행 1234-56-7890-123\n예금주: 푸드컴퍼니\n\n",
        'send_screenshot': "📸 После оплаты отправьте скриншот чека",
        'payment_received': "✅ Спасибо! Ваш платеж получен. Заказ передан на обработку.",
        'choose_quantity_btn': "🔢 Выбрать количество",
        'main_menu': "🏠 Главное меню",
        'features': "✨ Наши преимущества:",
        'feature1': "• 🚚 Быстрая доставка 30-45 мин",
        'feature2': "• 💳 Удобная оплата",
        'feature3': "• 🍽️ Свежие и вкусные блюда",
        'feature4': "• 🌍 Доставка по всему городу",
        'start_command': "🔄 Перезапустить бота"
    },
    'ko': {
        'welcome': "🍖 푸드 컴퍼니에 오신 것을 환영합니다!",
        'welcome_message': """🌟 <b>푸드 봇에 오신 것을 환영합니다!</b> 🌟

🍽️ 아늑한 요리의 세계로 여러분을 초대합니다!

여기서您可以:
• 📋 다양한 메뉴 확인하기
• 🛒 좋아하는 요리 장바구니에 담기
• 🚚 빠른 배달 주문하기
• 💳 편리한 결제 방법

계속하려면 언어를 선택하세요:""",
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
        'choose_quantity': "수량을 선택하세요:",
        'go_to_cart': "🛒 장바구니로 이동",
        'checkout_name': "📝 이름을 입력하세요:",
        'checkout_phone': "📞 전화번호를 입력하세요:",
        'checkout_address': "🏠 배달 주소를 입력하세요:",
        'payment_details': "💳 결제 정보:\n\n",
        'payment_amount': "결제 금액:",
        'bank_details': "🏦 은행 정보:\nKB국민은행 1234-56-7890-123\n예금주: 푸드컴퍼니\n\n",
        'send_screenshot': "📸 결제 후 스크린샷을 보내주세요",
        'payment_received': "✅ 감사합니다! 결제가 확인되었습니다. 주문이 처리 중입니다.",
        'choose_quantity_btn': "🔢 수량 선택",
        'main_menu': "🏠 메인 메뉴",
        'features': "✨ 우리의 장점:",
        'feature1': "• 🚚 빠른 배달 30-45분",
        'feature2': "• 💳 편리한 결제",
        'feature3': "• 🍽️ 신선하고 맛있는 요리",
        'feature4': "• 🌍 도시 전체 배달",
        'start_command': "🔄 봇 다시 시작"
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
             'image_file': 'borsch.jpg'},
            {'id': 2, 'category_id': 1, 'name_ru': 'Солянка', 'name_ko': '솔랸카', 'price': 8000, 'weight': '350г', 
             'image_file': 'solyanka.jpg'},
            {'id': 3, 'category_id': 1, 'name_ru': 'Шурпа', 'name_ko': '슈르파', 'price': 8000, 'weight': '450г',
             'image_file': 'shurpa.jpg'},
            {'id': 4, 'category_id': 1, 'name_ru': 'Мастава', 'name_ko': '마스타바', 'price': 8000, 'weight': '400г',
             'image_file': 'mastava.jpg'},
            {'id': 5, 'category_id': 1, 'name_ru': 'Харчо', 'name_ko': '카르초', 'price': 8000, 'weight': '350г',
             'image_file': 'harchyo.jpg'},
            {'id': 6, 'category_id': 1, 'name_ru': 'Основа для лагмана', 'name_ko': '라그먼의 기초', 'price': 8000, 'weight': '450г',
             'image_file': 'lagman.jpg'},
           
            # Вторые блюда
            {'id': 7, 'category_id': 2, 'name_ru': 'Тушенка говяжья', 'name_ko': '소고기 스튜', 'price': 10000, 'weight': '300г', 
             'image_file': 'toshonka_govyadina.jpg'},
            {'id': 8, 'category_id': 2, 'name_ru': 'Тушенка свинная', 'name_ko': '돼지고기 조림', 'price': 10000, 'weight': '300г',
             'image_file': 'tushonka_svinya.jpg'},
            {'id': 9, 'category_id': 2, 'name_ru': 'Гуляш', 'name_ko': '굴라시', 'price': 8000, 'weight': '350г', 
             'image_file': 'gulyash.jpg'},
            {'id': 10, 'category_id': 2, 'name_ru': 'Мясо с грибами', 'name_ko': '버섯을 곁들인 고기', 'price': 9000, 'weight': '350г',
             'image_file': 'meat_mushrooms.jpg'},
            {'id': 11, 'category_id': 2, 'name_ru': 'Мясо с картошкой', 'name_ko': '고기와 감자', 'price': 9000, 'weight': '320г',
             'image_file': 'meat_potatoes.jpg'},
            {'id': 12, 'category_id': 2, 'name_ru': 'Бефстроганов', 'name_ko': '비프 스트로가노프', 'price': 8000, 'weight': '320г', 
             'image_file': 'beef_stroganoff.jpg'},
            {'id': 13, 'category_id': 2, 'name_ru': 'Основа для Беша', 'name_ko': '베샤의 기초', 'price': 7000, 'weight': '320г',
             'image_file': 'besh_basis.jpg'},
            
            # Стейки
            {'id': 14, 'category_id': 3, 'name_ru': 'Томогавк', 'name_ko': '토마호크', 'price': 12000, 'weight': '500г', 
             'image_file': 'tomahawk.jpg'},
            {'id': 15, 'category_id': 3, 'name_ru': 'Рибай', 'name_ko': '립아이', 'price': 9500, 'weight': '400г', 
             'image_file': 'ribeye.jpg'},
            {'id': 16, 'category_id': 3, 'name_ru': 'Нью-Йорк', 'name_ko': '뉴욕 스테이크', 'price': 8500, 'weight': '350г', 
             'image_file': 'new_york.jpg'},
            {'id': 17, 'category_id': 3, 'name_ru': 'Т-бон', 'name_ko': '티본', 'price': 8500, 'weight': '350г',
             'image_file': 't_bone.jpg'}
        ]
        
        # Хранилище в памяти
        self.user_data_store = {}
        logging.info("✅ Бот инициализирован")

    def get_image_path(self, image_file):
        """Получить путь к изображению"""
        if not image_file:
            return None
        
        # Проверяем существование файла в папке images
        images_dir = os.path.join(os.path.dirname(__file__), 'images')
        image_path = os.path.join(images_dir, image_file)
        
        if os.path.exists(image_path):
            return image_path
        else:
            logging.warning(f"⚠️ Файл изображения не найден: {image_path}")
            return None

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
        """Команда /start - КРАСИВОЕ ПРИВЕТСТВИЕ"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        language = self.get_user_language(user_id)
        
        # Персонализированное приветствие
        welcome_text = f"👋 <b>Привет, {user_name}!</b>\n\n" if language == 'ru' else f"👋 <b>안녕하세요, {user_name}님!</b>\n\n"
        welcome_text += get_translation(language, 'welcome_message')
        
        # Добавляем преимущества
        welcome_text += f"\n\n{get_translation(language, 'features')}\n"
        welcome_text += f"{get_translation(language, 'feature1')}\n"
        welcome_text += f"{get_translation(language, 'feature2')}\n"
        welcome_text += f"{get_translation(language, 'feature3')}\n"
        welcome_text += f"{get_translation(language, 'feature4')}"
        
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
             InlineKeyboardButton("🇰🇷 한국어", callback_data="lang_ko")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def handle_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Смена языка"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_name = query.from_user.first_name
        language = query.data.split('_')[1]
        
        self.set_user_language(user_id, language)
        
        # Приветствие после выбора языка
        welcome_after_lang = f"👋 <b>Привет, {user_name}!</b>\n\n" if language == 'ru' else f"👋 <b>안녕하세요, {user_name}님!</b>\n\n"
        welcome_after_lang += get_translation(language, 'welcome')
        
        keyboard = [
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
            [InlineKeyboardButton("🛒 " + get_translation(language, 'cart'), callback_data="cart")],
            [InlineKeyboardButton("📞 " + get_translation(language, 'contacts'), callback_data="contacts")],
            [InlineKeyboardButton("🔄 " + get_translation(language, 'start_command'), callback_data="start_command")],
            [
                InlineKeyboardButton("🇰🇷 한국어", callback_data="lang_ko"),
                InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_after_lang,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def show_main_menu(self, query, language):
        """Показать главное меню"""
        user_name = query.from_user.first_name
        
        welcome_text = f"🍖 <b>Добро пожаловать, {user_name}!</b>" if language == 'ru' else f"🍖 <b>환영합니다, {user_name}님!</b>"
        
        keyboard = [
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
            [InlineKeyboardButton("🛒 " + get_translation(language, 'cart'), callback_data="cart")],
            [InlineKeyboardButton("📞 " + get_translation(language, 'contacts'), callback_data="contacts")],
            [InlineKeyboardButton("🔄 " + get_translation(language, 'start_command'), callback_data="start_command")],
            [
                InlineKeyboardButton("🇰🇷 한국어", callback_data="lang_ko"),
                InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
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
        
        # Сохраняем текущую категорию в context для кнопки "Назад"
        context.user_data['current_category'] = category_id
        
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
        
        # Сохраняем информацию о блюде в context.user_data
        context.user_data['selected_dish'] = {
            'id': dish['id'],
            'name_ru': dish['name_ru'],
            'name_ko': dish['name_ko'], 
            'price': dish['price'],
            'category_id': dish['category_id'],
            'image_file': dish.get('image_file', '')
        }
        context.user_data['quantity'] = 1  # Сбрасываем количество
        
        # Получаем текущую категорию из context или из блюда
        current_category = context.user_data.get('current_category', dish['category_id'])
        
        # Пытаемся показать картинку
        image_path = self.get_image_path(dish.get('image_file'))
        
        if image_path:
            try:
                # Создаем клавиатуру для перехода к выбору количества
                keyboard = [
                    [InlineKeyboardButton("🔢 " + get_translation(language, 'choose_quantity_btn'), callback_data="show_quantity")],
                    [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="back"),
                     InlineKeyboardButton("🛒 " + get_translation(language, 'cart'), callback_data="cart")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Текст для картинки
                caption = f"🍽️ <b>{name}</b>\n💰 {get_translation(language, 'price')} {dish['price']}won"
                if dish['weight']:
                    caption += f"\n⚖️ {dish['weight']}"
                caption += f"\n\n👇 Нажмите кнопку ниже чтобы выбрать количество"
                
                # Отправляем фото из файла как новое сообщение
                with open(image_path, 'rb') as photo:
                    await query.message.reply_photo(
                        photo=photo,
                        caption=caption,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
                return
                
            except Exception as e:
                logging.error(f"Ошибка загрузки изображения: {e}")
                # Если картинка не загрузилась, переходим к выбору количества
                pass
        
        # Если нет картинки или произошла ошибка, показываем выбор количества
        await self.show_quantity_selection(update, context, dish, language, current_category)

    async def show_quantity_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, dish, language, category_id=None):
        """Показать выбор количества"""
        query = update.callback_query
        user_id = query.from_user.id if query else update.effective_user.id
        
        name = dish['name_ko'] if language == 'ko' else dish['name_ru']
        
        # Если category_id не передан, берем из context или из блюда
        if category_id is None:
            category_id = context.user_data.get('current_category', dish['category_id'])
        
        # Текст для выбора количества
        quantity_text = f"🍽️ <b>{name}</b>\n💰 {get_translation(language, 'price')} {dish['price']}won"
        if dish['weight']:
            quantity_text += f"\n⚖️ {dish['weight']}"
        quantity_text += f"\n\n{get_translation(language, 'choose_quantity')}"
        
        # Клавиатура для выбора количества
        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data="decrease"),
                InlineKeyboardButton("1", callback_data="quantity_display"),
                InlineKeyboardButton("➕", callback_data="increase")
            ],
            [
                InlineKeyboardButton("🛒 " + get_translation(language, 'add_to_cart'), callback_data="add_to_cart"),
                InlineKeyboardButton("📦 " + get_translation(language, 'go_to_cart'), callback_data="cart")
            ],
            [
                InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="back"),
                InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            # Если есть query, редактируем сообщение
            try:
                await query.edit_message_text(
                    quantity_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            except telegram.error.BadRequest as e:
                if "Message is not modified" in str(e):
                    # Игнорируем ошибку "сообщение не изменено"
                    pass
                elif "There is no text in the message to edit" in str(e):
                    # Если пытаемся редактировать сообщение без текста (например, с фото)
                    await query.message.reply_text(
                        quantity_text,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
                else:
                    logging.error(f"Ошибка редактирования сообщения: {e}")
                    await query.message.reply_text(
                        quantity_text,
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )
        else:
            await update.message.reply_text(
                quantity_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )

    async def handle_show_quantity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопки перехода к выбору количества"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        dish_data = context.user_data.get('selected_dish')
        if not dish_data:
            await query.message.reply_text("❌ Ошибка: блюдо не найдено")
            return
        
        # Находим полные данные блюда
        dish = next((d for d in self.dishes if d['id'] == dish_data['id']), None)
        if not dish:
            await query.message.reply_text("❌ Ошибка: блюдо не найдено")
            return
        
        # Получаем категорию из context
        category_id = context.user_data.get('current_category', dish['category_id'])
        
        await self.show_quantity_selection(update, context, dish, language, category_id)

    async def handle_quantity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Изменение количества"""
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
            logging.error("❌ Блюдо потеряно в контексте при изменении количества!")
            await query.edit_message_text("❌ Ошибка: блюдо не найдено")
            return
        
        name = dish_data['name_ko'] if language == 'ko' else dish_data['name_ru']
        
        # Получаем категорию из context
        category_id = context.user_data.get('current_category', dish_data['category_id'])
        
        # Создаем клавиатуру с новым количеством
        keyboard = [
            [
                InlineKeyboardButton("➖", callback_data="decrease"),
                InlineKeyboardButton(str(new_quantity), callback_data="quantity_display"),
                InlineKeyboardButton("➕", callback_data="increase")
            ],
            [
                InlineKeyboardButton("🛒 " + get_translation(language, 'add_to_cart'), callback_data="add_to_cart"),
                InlineKeyboardButton("📦 " + get_translation(language, 'go_to_cart'), callback_data="cart")
            ],
            [
                InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="back"),
                InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Текст сообщения
        dish_text = f"🍽️ <b>{name}</b>\n💰 {get_translation(language, 'price')} {dish_data['price']}won\n\n{get_translation(language, 'choose_quantity')}"
        
        # Обновляем сообщение с обработкой ошибок
        try:
            await query.edit_message_text(
                dish_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except telegram.error.BadRequest as e:
            if "Message is not modified" in str(e):
                # Игнорируем ошибку "сообщение не изменено"
                pass
            elif "There is no text in the message to edit" in str(e):
                # Если пытаемся редактировать сообщение без текста
                await query.message.reply_text(
                    dish_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            else:
                logging.error(f"Ошибка обновления сообщения: {e}")
                await query.message.reply_text(
                    dish_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )

    async def handle_quantity_display(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Просто показывает текущее количество (не меняет его)"""
        query = update.callback_query
        await query.answer()  # Убираем "часики"

    async def handle_add_to_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавить в корзину"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        # Получаем данные о выбранном блюде из контекста
        dish_data = context.user_data.get('selected_dish')
        
        if not dish_data:
            logging.error("❌ Блюдо не найдено в контексте!")
            await query.edit_message_text("❌ Ошибка: блюдо не выбрано")
            return
        
        quantity = context.user_data.get('quantity', 1)
        
        # Получаем текущую корзину пользователя
        cart = self.get_user_cart(user_id)
        
        dish_key = str(dish_data['id'])  # Используем ID блюда как ключ
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
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
            [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        success_message = f"✅ <b>{name}</b> x{quantity} {get_translation(language, 'add_to_cart')}!"
        
        try:
            await query.edit_message_text(
                success_message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except telegram.error.BadRequest as e:
            if "There is no text in the message to edit" in str(e):
                await query.message.reply_text(
                    success_message,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            else:
                raise
    
    async def handle_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать корзину"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        cart = self.get_user_cart(user_id)
        
        if not cart:
            keyboard = [
                [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
                [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                await query.edit_message_text(
                    "🛒 " + get_translation(language, 'cart_empty'),
                    reply_markup=reply_markup
                )
            except telegram.error.BadRequest as e:
                if "There is no text in the message to edit" in str(e):
                    await query.message.reply_text(
                        "🛒 " + get_translation(language, 'cart_empty'),
                        reply_markup=reply_markup
                    )
            return
        
        cart_text = "🛒 <b>" + get_translation(language, 'cart_items') + "</b>\n\n"
        total = 0
        
        for item_id, item_data in cart.items():
            item_total = item_data['price'] * item_data['quantity']
            total += item_total
            cart_text += f"• {item_data['name']} x{item_data['quantity']} - {item_total}won\n"
        
        cart_text += f"\n💰 <b>{get_translation(language, 'total')} {total}won</b>"
        
        keyboard = [
            [InlineKeyboardButton("💳 " + get_translation(language, 'checkout'), callback_data="checkout")],
            [InlineKeyboardButton("🗑️ " + get_translation(language, 'clear_cart'), callback_data="clear_cart")],
            [
                InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu"),
                InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                cart_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except telegram.error.BadRequest as e:
            if "There is no text in the message to edit" in str(e):
                await query.message.reply_text(
                    cart_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
    
    async def handle_clear_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Очистить корзину"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        self.set_user_cart(user_id, {})
        
        keyboard = [
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
            [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                "🗑️ " + get_translation(language, 'cart_empty'),
                reply_markup=reply_markup
            )
        except telegram.error.BadRequest as e:
            if "There is no text in the message to edit" in str(e):
                await query.message.reply_text(
                    "🗑️ " + get_translation(language, 'cart_empty'),
                    reply_markup=reply_markup
                )
    
    async def handle_checkout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Оформление заказа"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        cart = self.get_user_cart(user_id)
        
        if not cart:
            keyboard = [
                [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
                [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                await query.edit_message_text(
                    "🛒 " + get_translation(language, 'cart_empty'),
                    reply_markup=reply_markup
                )
            except telegram.error.BadRequest as e:
                if "There is no text in the message to edit" in str(e):
                    await query.message.reply_text(
                        "🛒 " + get_translation(language, 'cart_empty'),
                        reply_markup=reply_markup
                    )
            return
        
        # Создаем сводку заказа
        order_summary = "📋 <b>" + get_translation(language, 'order_summary') + "</b>\n\n"
        total = 0
        
        for item_id, item_data in cart.items():
            item_total = item_data['price'] * item_data['quantity']
            total += item_total
            order_summary += f"• {item_data['name']} x{item_data['quantity']} - {item_total}won\n"
        
        order_summary += f"\n💰 <b>{get_translation(language, 'total')} {total}won</b>"
        order_summary += f"\n\n🚚 {get_translation(language, 'delivery_info')}"
        
        keyboard = [
            [InlineKeyboardButton("✅ " + get_translation(language, 'confirm_order'), callback_data="confirm_order")],
            [
                InlineKeyboardButton("🛒 " + get_translation(language, 'back'), callback_data="cart"),
                InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                order_summary,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except telegram.error.BadRequest as e:
            if "There is no text in the message to edit" in str(e):
                await query.message.reply_text(
                    order_summary,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
    
    async def handle_confirm_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение заказа"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        cart = self.get_user_cart(user_id)
        
        if not cart:
            keyboard = [
                [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
                [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            try:
                await query.edit_message_text(
                    "🛒 " + get_translation(language, 'cart_empty'),
                    reply_markup=reply_markup
                )
            except telegram.error.BadRequest as e:
                if "There is no text in the message to edit" in str(e):
                    await query.message.reply_text(
                        "🛒 " + get_translation(language, 'cart_empty'),
                        reply_markup=reply_markup
                    )
            return
        
        # Рассчитываем итоговую сумму
        total = sum(item_data['price'] * item_data['quantity'] for item_data in cart.values())
        
        # Создаем сообщение с реквизитами
        payment_message = get_translation(language, 'payment_details')
        payment_message += get_translation(language, 'bank_details')
        payment_message += f"💵 {get_translation(language, 'payment_amount')} <b>{total}won</b>\n\n"
        payment_message += get_translation(language, 'send_screenshot')
        
        keyboard = [
            [InlineKeyboardButton("✅ " + get_translation(language, 'payment_received'), callback_data="payment_done")],
            [
                InlineKeyboardButton("🛒 " + get_translation(language, 'cart'), callback_data="cart"),
                InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="back")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                payment_message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except telegram.error.BadRequest as e:
            if "There is no text in the message to edit" in str(e):
                await query.message.reply_text(
                    payment_message,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
    
    async def handle_payment_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка подтверждения оплаты"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        # Очищаем корзину после оплаты
        self.set_user_cart(user_id, {})
        
        keyboard = [[InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                "✅ " + get_translation(language, 'payment_received'),
                reply_markup=reply_markup
            )
        except telegram.error.BadRequest as e:
            if "There is no text in the message to edit" in str(e):
                await query.message.reply_text(
                    "✅ " + get_translation(language, 'payment_received'),
                    reply_markup=reply_markup
                )
    
    async def handle_contacts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать контакты"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        contacts_text = "📞 <b>Контакты</b>\n\n" if language == 'ru' else "📞 <b>연락처</b>\n\n"
        contacts_text += "📍 Адрес: Сеул, район Каннам\n" if language == 'ru' else "📍 주소: 서울 강남구\n"
        contacts_text += "📱 Телефон: +82-10-1234-5678\n" if language == 'ru' else "📱 전화: +82-10-1234-5678\n"
        contacts_text += "🕒 Время работы: 10:00 - 22:00\n" if language == 'ru' else "🕒 영업시간: 10:00 - 22:00\n"
        contacts_text += "📧 Email: info@foodcompany.kr" if language == 'ru' else "📧 이메일: info@foodcompany.kr"
        
        keyboard = [[InlineKeyboardButton(get_translation(language, 'back'), callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                contacts_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except telegram.error.BadRequest as e:
            if "There is no text in the message to edit" in str(e):
                await query.message.reply_text(
                    contacts_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
    
    async def handle_back(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Назад в главное меню"""
        query = update.callback_query
        await query.answer()
        
        await self.show_main_menu(query, self.get_user_language(query.from_user.id))

    async def handle_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопки перезапуска бота"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_name = query.from_user.first_name
        language = self.get_user_language(user_id)
        
        # Персонализированное приветствие
        welcome_text = f"👋 <b>Привет, {user_name}!</b>\n\n" if language == 'ru' else f"👋 <b>안녕하세요, {user_name}님!</b>\n\n"
        welcome_text += get_translation(language, 'welcome_message')
        
        # Добавляем преимущества
        welcome_text += f"\n\n{get_translation(language, 'features')}\n"
        welcome_text += f"{get_translation(language, 'feature1')}\n"
        welcome_text += f"{get_translation(language, 'feature2')}\n"
        welcome_text += f"{get_translation(language, 'feature3')}\n"
        welcome_text += f"{get_translation(language, 'feature4')}"
        
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
             InlineKeyboardButton("🇰🇷 한국어", callback_data="lang_ko")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка скриншотов оплаты"""
        user_id = update.effective_user.id
        language = self.get_user_language(user_id)
        
        # Отправляем подтверждение получения скриншота
        await update.message.reply_text(
            "✅ " + get_translation(language, 'payment_received'),
            reply_to_message_id=update.message.message_id
        )
        
        # Показываем главное меню
        keyboard = [
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
            [InlineKeyboardButton("🛒 " + get_translation(language, 'cart'), callback_data="cart")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            get_translation(language, 'main_menu'),
            reply_markup=reply_markup
        )

    def setup_handlers(self, application):
        """Настройка обработчиков"""
        # Команды
        application.add_handler(CommandHandler("start", self.start))
        
        # Обработчики callback-запросов
        application.add_handler(CallbackQueryHandler(self.handle_language, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.handle_menu, pattern="^menu$"))
        application.add_handler(CallbackQueryHandler(self.handle_category, pattern="^cat_"))
        application.add_handler(CallbackQueryHandler(self.handle_dish, pattern="^dish_"))
        application.add_handler(CallbackQueryHandler(self.handle_show_quantity, pattern="^show_quantity$"))
        application.add_handler(CallbackQueryHandler(self.handle_quantity, pattern="^(increase|decrease)$"))
        application.add_handler(CallbackQueryHandler(self.handle_quantity_display, pattern="^quantity_display$"))
        application.add_handler(CallbackQueryHandler(self.handle_add_to_cart, pattern="^add_to_cart$"))
        application.add_handler(CallbackQueryHandler(self.handle_cart, pattern="^cart$"))
        application.add_handler(CallbackQueryHandler(self.handle_clear_cart, pattern="^clear_cart$"))
        application.add_handler(CallbackQueryHandler(self.handle_checkout, pattern="^checkout$"))
        application.add_handler(CallbackQueryHandler(self.handle_confirm_order, pattern="^confirm_order$"))
        application.add_handler(CallbackQueryHandler(self.handle_payment_done, pattern="^payment_done$"))
        application.add_handler(CallbackQueryHandler(self.handle_contacts, pattern="^contacts$"))
        application.add_handler(CallbackQueryHandler(self.handle_back, pattern="^back$"))
        application.add_handler(CallbackQueryHandler(self.handle_start_command, pattern="^start_command$"))
        
        # Обработчик фото (скриншоты оплаты)
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))

def main():
    """Основная функция"""
    # Получаем токен бота из переменных окружения
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        logging.error("❌ BOT_TOKEN не установлен!")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Создаем бота и настраиваем обработчики
    bot = FoodBot()
    bot.setup_handlers(application)
    
    # Запускаем бота
    logging.info("🤖 Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()