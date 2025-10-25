translations = {
    'ru': {
        'welcome': "🍖 Добро пожаловать в ФУД! Выберите язык:",
        'menu': "Меню",
        'cart': "Корзина", 
        'contacts': "Контакты",
        'back': "Назад",
        'choose_category': "Выберите категорию:",
        'language_changed': "🌐 Язык изменен!"
    },
    'ko': {
        'welcome': "🍖 푸드에 오신 것을 환영합니다! 언어를 선택하세요:",
        'menu': "메뉴",
        'cart': "장바구니",
        'contacts': "연락처", 
        'back': "뒤로",
        'choose_category': "카테고리를 선택하세요:",
        'language_changed': "🌐 언어가 변경되었습니다!"
    }
}

def get_translation(language, key):
    return translations.get(language, translations['ru']).get(key, key)