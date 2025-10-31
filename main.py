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

# ID администратора (замените на ваш Telegram ID)
ADMIN_ID = 379494671  # Замените на реальный ID администратора

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
        'start_command': "🔄 Перезапустить бота",
        'enter_name': "📝 Пожалуйста, введите ваше имя:",
        'enter_phone': "📞 Теперь введите ваш номер телефона:",
        'enter_address': "🏠 Введите адрес доставки:",
        'order_sent_to_admin': "📨 Ваш заказ отправлен администратору. Ожидайте подтверждения.",
        'order_confirmed_by_admin': "✅ Ваш заказ подтвержден! Теперь вы можете произвести оплату.",
        'waiting_for_admin': "⏳ Ожидание подтверждения заказа администратором...",
        'admin_new_order': "🆕 НОВЫЙ ЗАКАЗ!\n\n",
        'admin_order_details': "Детали заказа:\n",
        'admin_customer_info': "Информация о клиенте:\n",
        'admin_confirm_button': "✅ Подтвердить заказ",
        'admin_reject_button': "❌ Отклонить заказ",
        'admin_order_confirmed': "✅ Заказ подтвержден. Клиенту отправлены реквизиты для оплаты.",
        'admin_order_rejected': "❌ Заказ отклонен.",
        'admin_payment_received': "💳 ПОСТУПИЛА ОПЛАТА!\n\n",
        'admin_confirm_payment': "✅ Подтвердить получение оплаты",
        'admin_payment_confirmed': "✅ Оплата подтверждена. Клиент уведомлен.",
        'order_rejected': "❌ К сожалению, ваш заказ был отклонен администратором. Пожалуйста, свяжитесь с нами для уточнения деталей.",
        'waiting_for_payment_confirmation': "⏳ Ожидание подтверждения оплаты администратором...",
        'payment_confirmed': "✅ Ваша оплата подтверждена! Ваш заказ принят. Пожалуйста, ожидайте звонка от нашего сотрудника.",
        'continue_shopping': "🛍️ Продолжить покупки"
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
        'start_command': "🔄 봇 다시 시작",
        'enter_name': "📝 이름을 입력해 주세요:",
        'enter_phone': "📞 전화번호를 입력해 주세요:",
        'enter_address': "🏠 배달 주소를 입력해 주세요:",
        'order_sent_to_admin': "📨 주문이 관리자에게 전송되었습니다. 확인을 기다려 주세요.",
        'order_confirmed_by_admin': "✅ 주문이 확인되었습니다! 이제 결제를 진행할 수 있습니다.",
        'waiting_for_admin': "⏳ 관리자의 주문 확인을 기다리는 중...",
        'admin_new_order': "🆕 새 주문!\n\n",
        'admin_order_details': "주문 세부 정보:\n",
        'admin_customer_info': "고객 정보:\n",
        'admin_confirm_button': "✅ 주문 확인",
        'admin_reject_button': "❌ 주문 거절",
        'admin_order_confirmed': "✅ 주문이 확인되었습니다. 고객에게 결제 정보가 전송되었습니다.",
        'admin_order_rejected': "❌ 주문이 거절되었습니다.",
        'admin_payment_received': "💳 결제 접수!\n\n",
        'admin_confirm_payment': "✅ 결제 확인",
        'admin_payment_confirmed': "✅ 결제가 확인되었습니다. 고객에게 알림이 전송되었습니다.",
        'order_rejected': "❌ 죄송합니다. 관리자에 의해 주문이 거절되었습니다. 자세한 내용은 문의해 주세요.",
        'waiting_for_payment_confirmation': "⏳ 관리자의 결제 확인을 기다리는 중...",
        'payment_confirmed': "✅ 결제가 확인되었습니다! 주문이 접수되었습니다. 직원의 연락을 기다려 주세요.",
        'continue_shopping': "🛍️ 쇼핑 계속하기"
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
            # ... остальные блюда (оставьте как есть)
        ]
        
        # Хранилище в памяти
        self.user_data_store = {}
        self.admin_orders = {}  # Хранилище заказов для администратора
        logging.info("✅ Бот инициализирован")

    # ... остальные методы (get_image_path, get_user_language, set_user_language, get_user_cart, set_user_cart) оставьте без изменений

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

    # ... все остальные методы до handle_checkout оставьте без изменений

    async def handle_checkout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Оформление заказа - начинаем сбор данных"""
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
        
        # Начинаем сбор данных о клиенте
        context.user_data['checkout_step'] = 'name'
        context.user_data['order_cart'] = cart  # Сохраняем корзину в контексте
        
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
        """Обработка текстового ввода при оформлении заказа"""
        user_id = update.effective_user.id
        language = self.get_user_language(user_id)
        text = update.message.text
        
        # Проверяем, находится ли пользователь в процессе оформления заказа
        checkout_step = context.user_data.get('checkout_step')
        
        if not checkout_step:
            # Если не в процессе оформления, игнорируем
            return
        
        if checkout_step == 'name':
            # Сохраняем имя и запрашиваем телефон
            context.user_data['customer_name'] = text
            context.user_data['checkout_step'] = 'phone'
            
            await update.message.reply_text(get_translation(language, 'enter_phone'))
            
        elif checkout_step == 'phone':
            # Сохраняем телефон и запрашиваем адрес
            context.user_data['customer_phone'] = text
            context.user_data['checkout_step'] = 'address'
            
            await update.message.reply_text(get_translation(language, 'enter_address'))
            
        elif checkout_step == 'address':
            # Сохраняем адрес и отправляем заказ администратору
            context.user_data['customer_address'] = text
            context.user_data['checkout_step'] = None
            
            # Отправляем заказ администратору
            await self.send_order_to_admin(update, context, user_id, language)

    async def send_order_to_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, language: str):
        """Отправка заказа администратору"""
        cart = context.user_data.get('order_cart', {})
        customer_name = context.user_data.get('customer_name', '')
        customer_phone = context.user_data.get('customer_phone', '')
        customer_address = context.user_data.get('customer_address', '')
        
        if not cart:
            await update.message.reply_text("❌ Ошибка: корзина пуста")
            return
        
        # Создаем сводку заказа
        order_summary = get_translation(language, 'admin_new_order')
        order_summary += get_translation(language, 'admin_order_details')
        
        total = 0
        for item_id, item_data in cart.items():
            item_total = item_data['price'] * item_data['quantity']
            total += item_total
            order_summary += f"• {item_data['name']} x{item_data['quantity']} - {item_total}won\n"
        
        order_summary += f"\n💰 {get_translation(language, 'total')} {total}won\n\n"
        order_summary += get_translation(language, 'admin_customer_info')
        order_summary += f"👤 Имя: {customer_name}\n"
        order_summary += f"📞 Телефон: {customer_phone}\n"
        order_summary += f"🏠 Адрес: {customer_address}\n"
        order_summary += f"👤 ID пользователя: {user_id}"
        
        # Сохраняем информацию о заказе для администратора
        order_id = f"order_{user_id}_{int(update.message.date.timestamp())}"
        self.admin_orders[order_id] = {
            'user_id': user_id,
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'customer_address': customer_address,
            'cart': cart,
            'total': total,
            'language': language,
            'status': 'pending'
        }
        
        # Клавиатура для администратора
        keyboard = [
            [
                InlineKeyboardButton(get_translation('ru', 'admin_confirm_button'), callback_data=f"admin_confirm_{order_id}"),
                InlineKeyboardButton(get_translation('ru', 'admin_reject_button'), callback_data=f"admin_reject_{order_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем заказ администратору
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=order_summary,
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения администратору: {e}")
            await update.message.reply_text("❌ Ошибка отправки заказа. Пожалуйста, попробуйте позже.")
            return
        
        # Уведомляем пользователя
        keyboard = [
            [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            get_translation(language, 'order_sent_to_admin'),
            reply_markup=reply_markup
        )

    async def handle_admin_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Администратор подтверждает заказ"""
        query = update.callback_query
        await query.answer()
        
        order_id = query.data.split('_')[2]
        order_data = self.admin_orders.get(order_id)
        
        if not order_data:
            await query.edit_message_text("❌ Заказ не найден")
            return
        
        # Обновляем статус заказа
        order_data['status'] = 'confirmed'
        
        # Уведомляем администратора
        await query.edit_message_text(
            get_translation('ru', 'admin_order_confirmed') + f"\n\nID заказа: {order_id}"
        )
        
        # Отправляем реквизиты для оплаты клиенту
        user_id = order_data['user_id']
        language = order_data['language']
        total = order_data['total']
        
        payment_message = get_translation(language, 'payment_details')
        payment_message += get_translation(language, 'bank_details')
        payment_message += f"💵 {get_translation(language, 'payment_amount')} <b>{total}won</b>\n\n"
        payment_message += get_translation(language, 'send_screenshot')
        
        keyboard = [
            [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=payment_message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения клиенту: {e}")

    async def handle_admin_reject(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Администратор отклоняет заказ"""
        query = update.callback_query
        await query.answer()
        
        order_id = query.data.split('_')[2]
        order_data = self.admin_orders.get(order_id)
        
        if not order_data:
            await query.edit_message_text("❌ Заказ не найден")
            return
        
        # Обновляем статус заказа
        order_data['status'] = 'rejected'
        
        # Уведомляем администратора
        await query.edit_message_text(
            get_translation('ru', 'admin_order_rejected') + f"\n\nID заказа: {order_id}"
        )
        
        # Уведомляем клиента
        user_id = order_data['user_id']
        language = order_data['language']
        
        keyboard = [
            [InlineKeyboardButton("🏠 " + get_translation(language, 'main_menu'), callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=get_translation(language, 'order_rejected'),
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения клиенту: {e}")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка скриншотов оплаты - отправка администратору"""
        user_id = update.effective_user.id
        language = self.get_user_language(user_id)
        
        # Ищем активный заказ пользователя
        user_order_id = None
        for order_id, order_data in self.admin_orders.items():
            if (order_data['user_id'] == user_id and 
                order_data['status'] in ['confirmed', 'payment_sent']):
                user_order_id = order_id
                break
        
        if not user_order_id:
            await update.message.reply_text(
                "❌ У вас нет активных заказов, ожидающих оплаты.",
                reply_to_message_id=update.message.message_id
            )
            return
        
        order_data = self.admin_orders[user_order_id]
        
        # Обновляем статус заказа
        order_data['status'] = 'payment_sent'
        
        # Отправляем скриншот администратору
        admin_message = get_translation('ru', 'admin_payment_received')
        admin_message += f"ID заказа: {user_order_id}\n"
        admin_message += f"👤 Клиент: {order_data['customer_name']}\n"
        admin_message += f"📞 Телефон: {order_data['customer_phone']}\n"
        admin_message += f"💰 Сумма: {order_data['total']}won\n\n"
        admin_message += "📸 Скриншот оплаты:"
        
        # Клавиатура для администратора
        keyboard = [
            [InlineKeyboardButton(get_translation('ru', 'admin_confirm_payment'), 
                                callback_data=f"admin_confirm_payment_{user_order_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Пересылаем фото администратору
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_message
            )
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=update.message.photo[-1].file_id,
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Ошибка отправки фото администратору: {e}")
            await update.message.reply_text("❌ Ошибка отправки скриншота. Пожалуйста, попробуйте позже.")
            return
        
        # Уведомляем пользователя
        await update.message.reply_text(
            get_translation(language, 'waiting_for_payment_confirmation'),
            reply_to_message_id=update.message.message_id
        )

    async def handle_admin_confirm_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Администратор подтверждает получение оплаты"""
        query = update.callback_query
        await query.answer()
        
        order_id = query.data.split('_')[3]
        order_data = self.admin_orders.get(order_id)
        
        if not order_data:
            await query.edit_message_text("❌ Заказ не найден")
            return
        
        # Обновляем статус заказа
        order_data['status'] = 'payment_confirmed'
        
        # Уведомляем администратора
        await query.edit_message_text(
            get_translation('ru', 'admin_payment_confirmed') + f"\n\nID заказа: {order_id}"
        )
        
        # Уведомляем клиента
        user_id = order_data['user_id']
        language = order_data['language']
        
        # Очищаем корзину пользователя
        self.set_user_cart(user_id, {})
        
        keyboard = [
            [InlineKeyboardButton("🍽️ " + get_translation(language, 'menu'), callback_data="menu")],
            [InlineKeyboardButton(get_translation(language, 'continue_shopping'), callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=get_translation(language, 'payment_confirmed'),
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения клиенту: {e}")

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
        application.add_handler(CallbackQueryHandler(self.handle_main_menu, pattern="^main_menu$"))
        application.add_handler(CallbackQueryHandler(self.handle_start_command, pattern="^start_command$"))
        
        # Новые обработчики для администратора
        application.add_handler(CallbackQueryHandler(self.handle_admin_confirm, pattern="^admin_confirm_"))
        application.add_handler(CallbackQueryHandler(self.handle_admin_reject, pattern="^admin_reject_"))
        application.add_handler(CallbackQueryHandler(self.handle_admin_confirm_payment, pattern="^admin_confirm_payment_"))
        
        # Обработчики для кнопок "Назад" из категорий
        application.add_handler(CallbackQueryHandler(self.handle_category_back, pattern="^cat_"))
        
        # Обработчик текстовых сообщений (для сбора данных при оформлении заказа)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_input))
        
        # Обработчик фото (скриншоты оплаты)
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))

    # ... остальные методы оставьте без изменений

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