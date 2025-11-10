import os
import logging
import time
import re
from datetime import datetime
import telegram.error
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ID группы для заказов (ЗАМЕНИТЕ НА РЕАЛЬНЫЙ ID)
GROUP_ID = -5083395375  # ID группы администраторов

# Переводы
TRANSLATIONS = {
    'ru': {
        'welcome': "🍖 Добро пожаловать в Home Food!",
        'welcome_message': """🌟 <b>Добро пожаловать в Home_Food-бот!</b> 🌟

🍽️ Благодарим Вас за то что заинтересовались нашей продукцией!
Сделайте заказ прямо сейчас и посветите секономленное время себе и семье! 

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
        'order_summary': "📋 Ваш заказ:",
        'delivery_info': "🚚 Доставка: 30-45 минут",
        'confirm_order': "✅ Подтвердить заказ",
        'choose_quantity': "Выберите количество:",
        'go_to_cart': "🛒 Перейти в корзину",
        'checkout_name': "📝 Введите ваше имя:",
        'checkout_phone': "📞 Введите ваш телефон:",
        'checkout_address': "🏠 Отправьте фото с адресом доставки:\n\n(Сфотографируйте бумажку с адресом или отправьте скриншот карты)",
        'payment_details': "💳 Реквизиты для оплаты:\n\n",
        'payment_amount': "Сумма к оплате:",
        'bank_details': "🏦 Банковские реквизиты:\n전북은행 (JEONBUK BANK)\n계좌번호: 9100053711589\n예금주: 01080281960\n\n",
        'send_screenshot': "📸 После оплаты отправьте скриншот чека в этот чат",
        'payment_received': "✅ Спасибо! Ваш платеж получен. Заказ передан на обработку.",
        'choose_quantity_btn': "🔢 Выбрать количество",
        'main_menu': "🏠 Главное меню",
        'features': "✨ Наши преимущества:",
        'feature1': "• 🚚 Быстрая доставка 30-45 мин",
        'feature2': "• 💳 Удобная оплата",
        'feature3': "• 🍽️ Свежие и вкусные блюда",
        'feature4': "• 🌍 Доставка по всему городу",
        'start_command': "🔄 Перезапустить бота",
        'enter_name': "📝 Пожалуйста, введите ваше имя:",
        'enter_phone': "📞 Теперь введите ваш номер телефона:",
        'enter_address': "🏠 Отправьте фото с адресом доставки:\n\n📸 <b>Сфотографируйте бумажку с адресом или отправьте скриншот карты</b>",
        'order_sent_to_admin': "✅ Заказ оформлен! Теперь произведите оплату по указанным реквизитам и отправьте скриншот чека.",
        'order_ready_for_payment': "💳 Произведите оплату по следующим реквизитам:\n\n",
        'order_preparing': "👨‍🍳 Ваш заказ принят в работу и готовится! Ожидайте доставки в течение 30-45 минут.",
        'group_new_order': "🆕 НОВЫЙ ЗАКАЗ\n\n",
        'group_order_details': "Детали заказа:\n",
        'group_customer_info': "Информация о клиенте:\n",
        'continue_shopping': "🛍️ Продолжить покупки",
        'payment_instructions': "💳 После оформления заказа вы автоматически получите реквизиты для оплаты. После оплаты отправьте скриншот чека в этот чат.",
        'admin_payment_received': "💰 АДМИНИСТРАТОР: Платеж получен",
        'admin_confirm_payment': "✅ Подтвердить оплату",
        'admin_reject_payment': "❌ Отклонить платеж",
        'payment_confirmed_by_admin': "🎉 Ваш платеж подтвержден администратором! Заказ готовится.",
        'payment_rejected_by_admin': "❌ Платеж не подтвержден. Пожалуйста, свяжитесь с поддержкой.",
        'waiting_admin_confirmation': "⏳ Ожидание подтверждения оплаты администратором...",
        'order_status_cooking': "👨‍🍳 Заказ готовится",
        'order_status_delivery': "🚚 Заказ в доставке",
        'order_status_completed': "✅ Заказ завершен",
        'order_not_found': "❌ Заказ не найден. Пожалуйста, оформите новый заказ.",
        'invalid_phone': "❌ Неверный формат телефона. Пожалуйста, введите номер в формате: +821012345678 или 01012345678",
        'invalid_name': "❌ Имя должно содержать только буквы и быть от 2 до 50 символов",
        'order_already_confirmed': "✅ Этот заказ уже подтвержден ранее",
        'order_already_rejected': "❌ Этот заказ уже отклонен ранее",
        'address_photo_received': "✅ Фото с адресом получено! Теперь отправьте скриншот оплаты.",
        'waiting_address_photo': "📸 Ожидание фото с адресом...",
        'please_send_address_photo': "❌ Пожалуйста, отправьте фото с адресом доставки"
    },
    'ko': {
        'welcome': "🍖 푸드 컴퍼니에 오신 것을 환영합니다!",
        'welcome_message': """🌟 <b>푸드 봇에 오신 것을 환영합니다!</b> 🌟

🍽️ 아늑한 요리의 세계로 여러분을 초대합니다!

여기서 вы можете:
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
        'order_summary': "📋 주문 내용:",
        'delivery_info': "🚚 배달: 30-45분",
        'confirm_order': "✅ 주문 확인",
        'choose_quantity': "수량을 선택하세요:",
        'go_to_cart': "🛒 장바구니로 이동",
        'checkout_name': "📝 이름을 입력하세요:",
        'checkout_phone': "📞 전화번호를 입력하세요:",
        'checkout_address': "🏠 배달 주소 사진을 보내주세요:\n\n(주소가 적힌 종이를 사진 찍어 보내주세요 또는 지도 스크린샷)",
        'payment_details': "💳 결제 정보:\n\n",
        'payment_amount': "결제 금액:",
        'bank_details': "🏦 은행 정보:\n전북은행 (JEONBUK BANK)\n계좌번호: 9100053711589\n예금주: 01080281960\n\n",
        'send_screenshot': "📸 결제 후 스크린샷을 이 채팅방에 보내주세요",
        'payment_received': "✅ 감사합니다! 결제가 확인되었습니다. 주문이 처리 중입니다.",
        'choose_quantity_btn': "🔢 수량 선택",
        'main_menu': "🏠 메인 메뉴",
        'features': "✨ 우리의 장점:",
        'feature1': "• 🚚 빠른 배달 30-45분",
        'feature2': "• 💳 편리한 결제",
        'feature3': "• 🍽️ 신선하고 맛있는 요리",
        'feature4': "• 🌍 도시 전체 배달",
        'start_command': "🔄 봇 다시 시작",
        'enter_name': "📝 이름을 입력해 주세요:",
        'enter_phone': "📞 전화번호를 입력해 주세요:",
        'enter_address': "🏠 배달 주소 사진을 보내주세요:\n\n📸 <b>주소가 적힌 종이를 사진 찍어 보내주세요 또는 지도 스크린샷</b>",
        'order_sent_to_admin': "✅ 주문이 완료되었습니다! 아래 정보로 결제를 진행하고 스크린샷을 보내주세요.",
        'order_ready_for_payment': "💳 다음 정보로 결제를 진행하세요:\n\n",
        'order_preparing': "👨‍🍳 주문이 접수되어 준비 중입니다! 30-45분 내로 배달을 기다려 주세요.",
        'group_new_order': "🆕 새 주문\n\n",
        'group_order_details': "주문 세부 정보:\n",
        'group_customer_info': "고객 정보:\n",
        'continue_shopping': "🛍️ 쇼핑 계속하기",
        'payment_instructions': "💳 주문 후 자동으로 결제 정보를 받게 됩니다. 결제 후 스크린샷을 이 채팅방에 보내주세요.",
        'admin_payment_received': "💰 관리자: 결제 확인 요청",
        'admin_confirm_payment': "✅ 결제 확인",
        'admin_reject_payment': "❌ 결제 거절",
        'payment_confirmed_by_admin': "🎉 관리자가 결제를 확인했습니다! 주문이 준비 중입니다.",
        'payment_rejected_by_admin': "❌ 결제가 확인되지 않았습니다. 지원팀에 문의해 주세요.",
        'waiting_admin_confirmation': "⏳ 관리자의 결제 확인을 기다리는 중...",
        'order_status_cooking': "👨‍🍳 주문 준비 중",
        'order_status_delivery': "🚚 배달 중",
        'order_status_completed': "✅ 주문 완료",
        'order_not_found': "❌ 주문을 찾을 수 없습니다. 새 주문을 해주세요.",
        'invalid_phone': "❌ 전화번호 형식이 잘못되었습니다. +821012345678 또는 01012345678 형식으로 입력해 주세요",
        'invalid_name': "❌ 이름은 2~50자의 문자만 포함해야 합니다",
        'order_already_confirmed': "✅ 이 주문은 이미 확인되었습니다",
        'order_already_rejected': "❌ 이 주문은 이미 거절되었습니다",
        'address_photo_received': "✅ 주소 사진을 받았습니다! 이제 결제 스크린샷을 보내주세요.",
        'waiting_address_photo': "📸 주소 사진을 기다리는 중...",
        'please_send_address_photo': "❌ 배달 주소 사진을 보내주세요"
    }
}

def get_translation(language, key):
    return TRANSLATIONS.get(language, TRANSLATIONS['ru']).get(key, key)

class FoodBot:
    def __init__(self):
        # Категории блюд
        self.categories = [
            {'id': 1, 'name_ru': '🍲 Первые блюда', 'name_ko': '🍲 첫 번째 요리'},
            {'id': 2, 'name_ru': '🍖 Вторые блюда', 'name_ko': '🍖 두 번째 요리'},
            {'id': 3, 'name_ru': '🥩 Стейки', 'name_ko': '🥩 스테이크'}
        ]
        
        # Блюда
        self.dishes = [
            # Первые блюда
            {'id': 1, 'category_id': 1, 'name_ru': 'Борщ', 'name_ko': '보르시', 'price': 8000, 'weight': '400г', 'image_file': 'borsch.jpg'},
            {'id': 2, 'category_id': 1, 'name_ru': 'Солянка', 'name_ko': '솔랸카', 'price': 8000, 'weight': '350г', 'image_file': 'solyanka.jpg'},
            {'id': 3, 'category_id': 1, 'name_ru': 'Шурпа', 'name_ko': '슈르파', 'price': 8000, 'weight': '450г', 'image_file': 'shurpa.jpg'},
            {'id': 4, 'category_id': 1, 'name_ru': 'Мастава', 'name_ko': '마스타바', 'price': 8000, 'weight': '400г', 'image_file': 'mastava.jpg'},
            {'id': 5, 'category_id': 1, 'name_ru': 'Харчо', 'name_ko': '카르초', 'price': 8000, 'weight': '350г', 'image_file': 'harchyo.jpg'},
            {'id': 6, 'category_id': 1, 'name_ru': 'Основа для лагмана', 'name_ko': '라그먼의 기초', 'price': 8000, 'weight': '450г', 'image_file': 'lagman.jpg'},
           
            # Вторые блюда
            {'id': 7, 'category_id': 2, 'name_ru': 'Тушенка говяжья', 'name_ko': '소고기 스튜', 'price': 10000, 'weight': '300г', 'image_file': 'toshonka_govyadina.jpg'},
            {'id': 8, 'category_id': 2, 'name_ru': 'Тушенка свинная', 'name_ko': '돼지고기 조림', 'price': 10000, 'weight': '300г', 'image_file': 'tushonka_svinya.jpg'},
            {'id': 9, 'category_id': 2, 'name_ru': 'Гуляш', 'name_ko': '굴라시', 'price': 8000, 'weight': '350г', 'image_file': 'gulyash.jpg'},
            {'id': 10, 'category_id': 2, 'name_ru': 'Мясо с грибами', 'name_ko': '버섯을 곁들인 고기', 'price': 9000, 'weight': '350г', 'image_file': 'meat_mushrooms.jpg'},
            {'id': 11, 'category_id': 2, 'name_ru': 'Мясо с картошкой', 'name_ko': '고기와 감자', 'price': 9000, 'weight': '320г', 'image_file': 'meat_potatoes.jpg'},
            {'id': 12, 'category_id': 2, 'name_ru': 'Бефстроганов', 'name_ko': '비프 스트로가노프', 'price': 8000, 'weight': '320г', 'image_file': 'beef_stroganoff.jpg'},
            {'id': 13, 'category_id': 2, 'name_ru': 'Основа для Беша', 'name_ko': '베샤의 기초', 'price': 7000, 'weight': '320г', 'image_file': 'besh_basis.jpg'},
            
            # Стейки
            {'id': 14, 'category_id': 3, 'name_ru': 'Томогавк', 'name_ko': '토마호크', 'price': 12000, 'weight': '500г', 'image_file': 'tomahawk.jpg'},
            {'id': 15, 'category_id': 3, 'name_ru': 'Рибай', 'name_ko': '립아이', 'price': 9500, 'weight': '400г', 'image_file': 'ribeye.jpg'},
            {'id': 16, 'category_id': 3, 'name_ru': 'Нью-Йорк', 'name_ko': '뉴욕 스테이크', 'price': 8500, 'weight': '350г', 'image_file': 'new_york.jpg'},
            {'id': 17, 'category_id': 3, 'name_ru': 'Т-бон', 'name_ko': '티본', 'price': 8500, 'weight': '350г', 'image_file': 't_bone.jpg'}
        ]
        
        # Хранилище данных
        self.user_data_store = {}
        self.user_orders = {}
        self.order_counter = 0
        self.admin_messages = {}
        logging.info("✅ Бот инициализирован")

    def get_image_path(self, image_file):
        """Получить путь к изображению"""
        if not image_file:
            return None
        images_dir = os.path.join(os.path.dirname(__file__), 'images')
        image_path = os.path.join(images_dir, image_file)
        if os.path.exists(image_path):
            return image_path
        else:
            logging.warning(f"⚠️ Файл изображения не найден: {image_path}")
            return None

    def get_user_language(self, user_id):
        """Получить язык пользователя"""
        user_data = self.user_data_store.get(user_id, {})
        language = user_data.get('language', 'ru')
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

    def create_order_id(self):
        """Создать уникальный ID заказа"""
        self.order_counter += 1
        timestamp = int(time.time())
        order_id = f"order_{timestamp}_{self.order_counter}"
        logging.info(f"🆕 Сгенерирован order_id: {order_id}")
        return order_id

    def validate_phone(self, phone):
        """Валидация номера телефона"""
        pattern = r'^(\+82|82)?\-?0?10\-?\d{4}\-?\d{4}$'
        return re.match(pattern, phone.replace(' ', '')) is not None

    def validate_name(self, name):
        """Валидация имени"""
        return 2 <= len(name) <= 50 and all(c.isalpha() or c.isspace() for c in name)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        language = self.get_user_language(user_id)
        
        welcome_text = f"👋 <b>Привет, {user_name}!</b>\n\n" if language == 'ru' else f"👋 <b>안녕하세요, {user_name}님!</b>\n\n"
        welcome_text += get_translation(language, 'welcome_message')
        
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
        
        context.user_data['selected_dish'] = {
            'id': dish['id'],
            'name_ru': dish['name_ru'],
            'name_ko': dish['name_ko'], 
            'price': dish['price'],
            'category_id': dish['category_id'],
            'image_file': dish.get('image_file', '')
        }
        context.user_data['quantity'] = 1
        
        current_category = context.user_data.get('current_category', dish['category_id'])
        
        image_path = self.get_image_path(dish.get('image_file'))
        
        if image_path:
            try:
                keyboard = [
                    [InlineKeyboardButton("🔢 " + get_translation(language, 'choose_quantity_btn'), callback_data="show_quantity")],
                    [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="main_menu"),
                     InlineKeyboardButton("🛒 " + get_translation(language, 'cart'), callback_data="cart")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                caption = f"🍽️ <b>{name}</b>\n💰 {get_translation(language, 'price')} {dish['price']}won"
                if dish['weight']:
                    caption += f"\n⚖️ {dish['weight']}"
                caption += f"\n\n👇 Нажмите кнопку ниже чтобы выбрать количество"
                
                with open(image_path, 'rb') as photo:
                    await query.message.reply_photo(
                        photo=photo,
                        caption=caption,
                        parse_mode='HTML'
                    )
                
                await query.message.reply_text(
                    "👇 Выберите действие:",
                    reply_markup=reply_markup
                )
                return
                
            except Exception as e:
                logging.error(f"Ошибка загрузки изображения: {e}")
        
        await self.show_quantity_selection(update, context, dish, language, current_category)

    async def show_quantity_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, dish, language, category_id=None):
        """Показать выбор количества"""
        query = update.callback_query
        user_id = query.from_user.id if query else update.effective_user.id
        
        name = dish['name_ko'] if language == 'ko' else dish['name_ru']
        
        if category_id is None:
            category_id = context.user_data.get('current_category', dish['category_id'])
        
        quantity_text = f"🍽️ <b>{name}</b>\n💰 {get_translation(language, 'price')} {dish['price']}won"
        if dish['weight']:
            quantity_text += f"\n⚖️ {dish['weight']}"
        quantity_text += f"\n\n{get_translation(language, 'choose_quantity')}"
        
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
                InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="main_menu"),
                InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query:
            try:
                await query.edit_message_text(
                    quantity_text,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            except telegram.error.BadRequest as e:
                if "Message is not modified" in str(e):
                    pass
                elif "There is no text in the message to edit" in str(e):
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
        
        dish = next((d for d in self.dishes if d['id'] == dish_data['id']), None)
        if not dish:
            await query.message.reply_text("❌ Ошибка: блюдо не найдено")
            return
        
        category_id = context.user_data.get('current_category', dish['category_id'])
        await self.show_quantity_selection(update, context, dish, language, category_id)

    async def handle_quantity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Изменение количества"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        current_quantity = context.user_data.get('quantity', 1)
        
        if query.data == "increase":
            new_quantity = current_quantity + 1
        elif query.data == "decrease" and current_quantity > 1:
            new_quantity = current_quantity - 1
        else:
            new_quantity = current_quantity
        
        context.user_data['quantity'] = new_quantity
        
        dish_data = context.user_data.get('selected_dish')
        if not dish_data:
            logging.error("❌ Блюдо потеряно в контексте при изменении количества!")
            await query.edit_message_text("❌ Ошибка: блюдо не найдено")
            return
        
        name = dish_data['name_ko'] if language == 'ko' else dish_data['name_ru']
        category_id = context.user_data.get('current_category', dish_data['category_id'])
        
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
                InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="main_menu"),
                InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        dish_text = f"🍽️ <b>{name}</b>\n💰 {get_translation(language, 'price')} {dish_data['price']}won\n\n{get_translation(language, 'choose_quantity')}"
        
        try:
            await query.edit_message_text(
                dish_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except telegram.error.BadRequest as e:
            if "Message is not modified" in str(e):
                pass
            elif "There is no text in the message to edit" in str(e):
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
        """Просто показывает текущее количество"""
        query = update.callback_query
        await query.answer()

    async def handle_add_to_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Добавить в корзину"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        dish_data = context.user_data.get('selected_dish')
        if not dish_data:
            logging.error("❌ Блюдо не найдено в контексте!")
            await query.edit_message_text("❌ Ошибка: блюдо не выбрано")
            return
        
        quantity = context.user_data.get('quantity', 1)
        cart = self.get_user_cart(user_id)
        
        dish_key = str(dish_data['id'])
        name = dish_data['name_ko'] if language == 'ko' else dish_data['name_ru']
        
        if dish_key in cart:
            cart[dish_key]['quantity'] += quantity
        else:
            cart[dish_key] = {
                'name': name,
                'price': dish_data['price'],
                'quantity': quantity
            }
        
        self.set_user_cart(user_id, cart)
        
        keyboard = [
            [InlineKeyboardButton("🛒 " + get_translation(language, 'cart'), callback_data="cart")],
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
            [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="main_menu")]
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
                [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="main_menu")]
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
                InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="main_menu")
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
            [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="main_menu")]
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
                [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="main_menu")]
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
        
        context.user_data['checkout_step'] = 'name'
        context.user_data['order_cart'] = cart.copy()
        
        keyboard = [[InlineKeyboardButton(get_translation(language, 'back'), callback_data="cart")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(
                get_translation(language, 'enter_name'),
                reply_markup=reply_markup
            )
        except telegram.error.BadRequest as e:
            if "There is no text in the message to edit" in str(e):
                await query.message.reply_text(
                    get_translation(language, 'enter_name'),
                    reply_markup=reply_markup
                )

    async def handle_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстового ввода"""
        user_id = update.effective_user.id
        language = self.get_user_language(user_id)
        text = update.message.text.strip()
        
        checkout_step = context.user_data.get('checkout_step')
        if not checkout_step:
            return
        
        if checkout_step == 'name':
            if not self.validate_name(text):
                await update.message.reply_text(get_translation(language, 'invalid_name'))
                return
                
            context.user_data['customer_name'] = text
            context.user_data['checkout_step'] = 'phone'
            await update.message.reply_text(get_translation(language, 'enter_phone'))
            
        elif checkout_step == 'phone':
            if not self.validate_phone(text):
                await update.message.reply_text(get_translation(language, 'invalid_phone'))
                return
                
            context.user_data['customer_phone'] = text
            context.user_data['checkout_step'] = 'address'
            await update.message.reply_text(
                get_translation(language, 'enter_address'),
                parse_mode='HTML'
            )

    async def handle_address_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка фото с адресом"""
        user_id = update.effective_user.id
        language = self.get_user_language(user_id)
        
        # Проверяем, находится ли пользователь на этапе ввода адреса
        checkout_step = context.user_data.get('checkout_step')
        if checkout_step != 'address':
            return
        
        # Сохраняем file_id фото адреса
        context.user_data['address_photo_id'] = update.message.photo[-1].file_id
        context.user_data['checkout_step'] = None
        
        # Уведомляем пользователя
        await update.message.reply_text(
            get_translation(language, 'address_photo_received'),
            reply_to_message_id=update.message.message_id
        )
        
        # Переходим к отправке реквизитов
        await self.send_payment_details(update, context, user_id, language)

    async def send_payment_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, language: str):
        """Отправка реквизитов для оплаты"""
        cart = context.user_data.get('order_cart', {})
        customer_name = context.user_data.get('customer_name', '')
        customer_phone = context.user_data.get('customer_phone', '')
        address_photo_id = context.user_data.get('address_photo_id')
        
        if not cart:
            await update.message.reply_text("❌ Ошибка: корзина пуста")
            return
        
        if not address_photo_id:
            await update.message.reply_text(get_translation(language, 'please_send_address_photo'))
            context.user_data['checkout_step'] = 'address'
            return
        
        total = 0
        order_details = ""
        for item_id, item_data in cart.items():
            item_total = item_data['price'] * item_data['quantity']
            total += item_total
            order_details += f"• {item_data['name']} x{item_data['quantity']} - {item_total}won\n"
        
        order_id = self.create_order_id()
        
        logging.info(f"📦 СОЗДАНИЕ ЗАКАЗА {order_id}:")
        logging.info(f"   👤 User ID: {user_id}")
        logging.info(f"   📞 Телефон: {customer_phone}")
        logging.info(f"   🏠 Адрес: фото отправлено")
        logging.info(f"   🛒 Товаров: {len(cart)}")
        logging.info(f"   💰 Сумма: {total}")
        
        self.user_orders[order_id] = {
            'user_id': user_id,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'address_photo_id': address_photo_id,
            'cart': cart.copy(),
            'total': total,
            'language': language,
            'status': 'waiting_payment',
            'payment_status': 'pending',
            'created_at': time.time(),
            'order_id': order_id
        }
        
        logging.info(f"📋 ВСЕ АКТИВНЫЕ ЗАКАЗЫ: {list(self.user_orders.keys())}")
        
        order_confirmation = get_translation(language, 'order_sent_to_admin')
        order_confirmation += f"\n\n📋 {get_translation(language, 'order_summary')}\n{order_details}"
        order_confirmation += f"\n💰 {get_translation(language, 'total')} {total}won"
        order_confirmation += f"\n\n📞 {get_translation(language, 'send_screenshot')}"
        order_confirmation += f"\n\n🆔 ID заказа: {order_id}"
        
        payment_message = get_translation(language, 'order_ready_for_payment')
        payment_message += get_translation(language, 'bank_details')
        payment_message += f"💵 {get_translation(language, 'payment_amount')} <b>{total}won</b>"
        payment_message += f"\n\n🆔 <b>ID заказа: {order_id}</b>"
        payment_message += f"\n\n💡 <i>Обязательно укажите ID заказа при оплате!</i>"
        
        try:
            await update.message.reply_text(order_confirmation)
            await update.message.reply_text(
                payment_message,
                parse_mode='HTML'
            )
            logging.info(f"✅ Реквизиты отправлены пользователю {user_id}, заказ {order_id}")
            
        except Exception as e:
            logging.error(f"❌ Ошибка отправки реквизитов пользователю {user_id}: {e}")
            await update.message.reply_text("❌ Ошибка оформления заказа. Пожалуйста, попробуйте позже.")

    async def handle_payment_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка скриншотов оплаты"""
        user_id = update.effective_user.id
        language = self.get_user_language(user_id)
        
        logging.info(f"🔍 ПОИСК ЗАКАЗА ДЛЯ USER {user_id}")
        logging.info(f"📋 ДОСТУПНЫЕ ЗАКАЗЫ: {list(self.user_orders.keys())}")
        
        user_order_id = None
        order_data = None
        
        for order_id, order in self.user_orders.items():
            logging.info(f"   🔎 Проверка заказа {order_id}: user_id={order.get('user_id')}, status={order.get('status')}")
            if (order.get('user_id') == user_id and 
                order.get('status') in ['waiting_payment', 'payment_sent']):
                user_order_id = order_id
                order_data = order
                logging.info(f"   ✅ НАЙДЕН ПОДХОДЯЩИЙ ЗАКАЗ: {user_order_id}")
                break
        
        if not user_order_id:
            logging.error(f"❌ ЗАКАЗ НЕ НАЙДЕН для пользователя {user_id}")
            logging.error(f"   📋 Все заказы: {self.user_orders}")
            await update.message.reply_text(
                get_translation(language, 'order_not_found'),
                reply_to_message_id=update.message.message_id
            )
            return
        
        order_data['status'] = 'payment_sent'
        order_data['payment_status'] = 'waiting_confirmation'
        order_data['screenshot_sent_at'] = time.time()
        order_data['payment_photo_id'] = update.message.photo[-1].file_id
        
        group_message = "🆕 <b>НОВЫЙ ЗАКАЗ - ОЖИДАЕТ ПОДТВЕРЖДЕНИЯ</b>\n\n"
        group_message += "👤 <b>Информация о клиенте:</b>\n"
        group_message += f"   • Имя: {order_data['customer_name']}\n"
        group_message += f"   • Телефон: {order_data['customer_phone']}\n"
        group_message += f"   • Язык: {'Русский' if order_data['language'] == 'ru' else 'Корейский'}\n\n"
        
        group_message += "📋 <b>Детали заказа:</b>\n"
        total = 0
        for item_id, item_data in order_data['cart'].items():
            item_total = item_data['price'] * item_data['quantity']
            total += item_total
            group_message += f"   • {item_data['name']} x{item_data['quantity']} - {item_total}won\n"
        
        group_message += f"\n💰 <b>Итого: {total}won</b>\n"
        group_message += f"🆔 <b>ID заказа: {user_order_id}</b>\n"
        group_message += f"⏰ Время заказа: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}\n"
        group_message += f"👤 User ID: {user_id}\n"
        
        admin_keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Подтвердить оплату", 
                    callback_data=f"admin_confirm_{user_order_id}"
                ),
                InlineKeyboardButton(
                    "❌ Отклонить платеж", 
                    callback_data=f"admin_reject_{user_order_id}"
                )
            ]
        ]
        admin_reply_markup = InlineKeyboardMarkup(admin_keyboard)
        
        try:
            # Отправляем текстовое сообщение в группу
            admin_message = await context.bot.send_message(
                chat_id=GROUP_ID,
                text=group_message,
                reply_markup=admin_reply_markup,
                parse_mode='HTML'
            )
            
            # Отправляем фото адреса в группу
            await context.bot.send_photo(
                chat_id=GROUP_ID,
                photo=order_data['address_photo_id'],
                caption=f"🏠 Адрес доставки для заказа {user_order_id}",
                reply_to_message_id=admin_message.message_id
            )
            
            # Отправляем скриншот оплаты в группу
            await context.bot.send_photo(
                chat_id=GROUP_ID,
                photo=order_data['payment_photo_id'],
                caption=f"📸 Скриншот оплаты для заказа {user_order_id}",
                reply_to_message_id=admin_message.message_id
            )
            
            self.admin_messages[user_order_id] = {
                'message_id': admin_message.message_id,
                'user_id': user_id
            }
            
            logging.info(f"✅ Заказ {user_order_id} отправлен в группу администраторов")
            
            await update.message.reply_text(
                f"📸 {get_translation(language, 'waiting_admin_confirmation')}\n\n"
                f"🆔 Ваш ID заказа: {user_order_id}\n"
                f"⏳ Ожидайте подтверждения оплаты администратором...",
                reply_to_message_id=update.message.message_id
            )
            
        except Exception as e:
            logging.error(f"❌ Ошибка отправки заказа в группу: {e}")
            await update.message.reply_text(
                "❌ Ошибка отправки заказа. Пожалуйста, попробуйте позже.",
                reply_to_message_id=update.message.message_id
            )

    async def handle_admin_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка подтверждения оплаты администратором"""
        query = update.callback_query
        await query.answer()
        
        logging.info(f"🔧 ОБРАБОТКА АДМИН КОМАНДЫ: {query.data}")
        logging.info(f"   👤 Админ: {query.from_user.first_name} (ID: {query.from_user.id})")
        logging.info(f"   💬 Chat ID: {query.message.chat.id}")
        logging.info(f"   📋 Все заказы: {list(self.user_orders.keys())}")
        
        if query.message.chat.id != GROUP_ID:
            await query.message.reply_text("❌ Эта команда доступна только в группе администраторов")
            return
        
        try:
            parts = query.data.split('_')
            logging.info(f"🔍 Части callback_data: {parts}")
            
            if len(parts) < 3:
                logging.error(f"❌ Неверный формат callback_data: {query.data}")
                await query.edit_message_text("❌ Ошибка: неверный формат команды")
                return
            
            action = parts[1]
            order_id_parts = parts[2:]
            order_id = '_'.join(order_id_parts)
            
            logging.info(f"✅ Распарсено: action={action}, order_id={order_id}")
            
        except Exception as e:
            logging.error(f"❌ Ошибка парсинга callback_data: {e}")
            await query.edit_message_text("❌ Ошибка обработки команды")
            return
        
        logging.info(f"🔍 ПОИСК ЗАКАЗА {order_id}")
        
        if order_id not in self.user_orders:
            logging.error(f"❌ Заказ {order_id} не найден в системе!")
            logging.error(f"   📋 Доступные заказы: {list(self.user_orders.keys())}")
            await query.edit_message_text(f"❌ Заказ {order_id} не найден в системе!")
            return
        
        order_data = self.user_orders[order_id]
        user_id = order_data['user_id']
        language = order_data['language']
        
        logging.info(f"✅ Заказ найден: {order_id}, user_id: {user_id}, статус: {order_data.get('status')}")
        
        if action == 'confirm':
            if order_data.get('payment_status') == 'confirmed':
                await query.answer(get_translation('ru', 'order_already_confirmed'), show_alert=True)
                return
                
            order_data['payment_status'] = 'confirmed'
            order_data['status'] = 'preparing'
            order_data['confirmed_at'] = time.time()
            order_data['confirmed_by'] = query.from_user.first_name
            order_data['confirmed_by_id'] = query.from_user.id
            
            original_text = query.message.text
            clean_text = original_text.split('\n\n🎉')[0].split('\n\n❌')[0]
            
            confirmed_message = clean_text + f"\n\n🎉 <b>ОПЛАТА ПОДТВЕРЖДЕНА</b>\n" \
                                          f"✅ Подтвердил: {query.from_user.first_name}\n" \
                                          f"⏰ Время: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}\n" \
                                          f"📦 Статус: Готовится"
            
            try:
                await query.edit_message_text(
                    confirmed_message,
                    parse_mode='HTML'
                )
                
                user_message = f"🎉 <b>{get_translation(language, 'payment_confirmed_by_admin')}</b>\n\n" \
                              f"✅ <b>Ваш заказ подтвержден!</b>\n" \
                              f"🆔 ID заказа: {order_id}\n" \
                              f"💰 Сумма: {order_data['total']}won\n" \
                              f"👨‍🍳 {get_translation(language, 'order_preparing')}\n" \
                              f"⏰ Время подтверждения: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}"
                
                await context.bot.send_message(
                    chat_id=user_id,
                    text=user_message,
                    parse_mode='HTML'
                )
                
                self.set_user_cart(user_id, {})
                
                logging.info(f"✅ Платеж для заказа {order_id} подтвержден администратором {query.from_user.first_name}")
                
            except Exception as e:
                logging.error(f"❌ Ошибка при подтверждении заказа {order_id}: {e}")
                
        elif action == 'reject':
            if order_data.get('payment_status') == 'rejected':
                await query.answer(get_translation('ru', 'order_already_rejected'), show_alert=True)
                return
                
            order_data['payment_status'] = 'rejected'
            order_data['status'] = 'payment_rejected'
            order_data['rejected_at'] = time.time()
            order_data['rejected_by'] = query.from_user.first_name
            
            original_text = query.message.text
            clean_text = original_text.split('\n\n🎉')[0].split('\n\n❌')[0]
            
            rejected_message = clean_text + f"\n\n❌ <b>ОПЛАТА ОТКЛОНЕНА</b>\n" \
                                         f"❌ Отклонил: {query.from_user.first_name}\n" \
                                         f"⏰ Время: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}\n" \
                                         f"💬 Статус: Требуется проверка"
            
            try:
                await query.edit_message_text(
                    rejected_message,
                    parse_mode='HTML'
                )
                
                user_message = f"❌ <b>{get_translation(language, 'payment_rejected_by_admin')}</b>\n\n" \
                              f"🆔 ID заказа: {order_id}\n" \
                              f"💰 Сумма: {order_data['total']}won\n" \
                              f"📞 Пожалуйста, свяжитесь с поддержкой для уточнения деталей."
                
                await context.bot.send_message(
                    chat_id=user_id,
                    text=user_message,
                    parse_mode='HTML'
                )
                
                logging.info(f"❌ Платеж для заказа {order_id} отклонен администратором {query.from_user.first_name}")
                
            except Exception as e:
                logging.error(f"❌ Ошибка при отклонении заказа {order_id}: {e}")
        else:
            logging.error(f"❌ Неизвестное действие: {action}")
            await query.edit_message_text("❌ Неизвестное действие")

    async def handle_contacts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать контакты"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        contacts_text = "📞 <b>Контакты</b>\n\n" if language == 'ru' else "📞 <b>연락처</b>\n\n"
        contacts_text += "📱 Телефон: 01080281960\n" if language == 'ru' else "📱 전화: 01080281960\n"
        contacts_text += "🕒 Время работы: 24Hours/7Days\n" if language == 'ru' else "🕒 영업시간: 24Hours/7Days\n"
        
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

    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопки Главное меню"""
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
        
        welcome_text = f"👋 <b>Привет, {user_name}!</b>\n\n" if language == 'ru' else f"👋 <b>안녕하세요, {user_name}님!</b>\n\n"
        welcome_text += get_translation(language, 'welcome_message')
        
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

    async def handle_category_back(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопки Назад из категории"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        language = self.get_user_language(user_id)
        
        callback_data = query.data
        if callback_data.startswith("cat_"):
            category_id = int(callback_data.split("_")[1])
            
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

    def setup_handlers(self, application):
        """Настройка обработчиков"""
        application.add_handler(CommandHandler("start", self.start))
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
        application.add_handler(CallbackQueryHandler(self.handle_contacts, pattern="^contacts$"))
        application.add_handler(CallbackQueryHandler(self.handle_back, pattern="^back$"))
        application.add_handler(CallbackQueryHandler(self.handle_main_menu, pattern="^main_menu$"))
        application.add_handler(CallbackQueryHandler(self.handle_start_command, pattern="^start_command$"))
        application.add_handler(CallbackQueryHandler(self.handle_admin_confirmation, pattern="^admin_"))
        application.add_handler(CallbackQueryHandler(self.handle_category_back, pattern="^cat_"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_input))
        
        # Раздельные обработчики для фото адреса и фото оплаты
        application.add_handler(MessageHandler(
            filters.PHOTO & filters.ChatType.PRIVATE, 
            self.handle_photo_message
        ))

    async def handle_photo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка всех фото сообщений"""
        user_id = update.effective_user.id
        checkout_step = context.user_data.get('checkout_step')
        
        if checkout_step == 'address':
            # Это фото адреса
            await self.handle_address_photo(update, context)
        else:
            # Это фото оплаты
            await self.handle_payment_photo(update, context)

def main():
    """Основная функция"""
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        logging.error("❌ BOT_TOKEN не установлен!")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    bot = FoodBot()
    bot.setup_handlers(application)
    
    logging.info("🤖 Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()