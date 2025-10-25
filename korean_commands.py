# korean_commands.py - Дополнительные команды для корейских пользователей

korean_help_text = {
    'ru': """
🤖 **Команды бота:**

/start - Главное меню
/menu - Посмотреть меню  
/cart - Корзина
/voice - Голосовой заказ
/lang - Сменить язык
/help - Помощь

📞 **Контакты:**
Телефон: +82 10XXXX-XXXX
Адрес: Ansan
    """,
    
    'ko': """
🤖 **봇 명령어:**

/start - 메인 메뉴
/menu - 메뉴 보기
/cart - 장바구니
/voice - 음성 주문
/lang - 언어 변경
/help - 도움말

📞 **연락처:**
전화: +7 XXX XXX-XX-XX
주소: 모스크바, 프리메르나야 거리
    """,
    
    'en': """
🤖 **Bot Commands:**

/start - Main menu
/menu - View menu
/cart - Cart
/voice - Voice order
/lang - Change language
/help - Help

📞 **Contacts:**
Phone: +7 XXX XXX-XX-XX
Address: Moscow, Primernaya st.
    """
}

async def handle_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /help"""
    user_id = update.effective_user.id
    language = context.bot.get_user_language(user_id)
    
    await update.message.reply_text(
        korean_help_text[language],
        parse_mode='Markdown'
    )

async def handle_lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /lang"""
    user_id = update.effective_user.id
    language = context.bot.get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🇰🇷 한국어", callback_data="language_ko"),
         In