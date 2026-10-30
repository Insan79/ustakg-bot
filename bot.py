import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# Вставьте сюда ваш токен от BotFather
TOKEN = "9263148489:AAGL-1gkpgPKbC5yHnG-5Hja3JHcnz4ICWk"

# Ваш ID в Telegram, куда будут приходить чеки на подтверждение (узнать свой ID можно у @userinfobot)
ADMIN_ID = 123456789  # ЗАМЕНИТЕ НА СВОЙ TELEGRAM ID!

# Список ваших 15 гайдов с ценами в сомах и файлами (пути к PDF)
GUIDES = {
    "g1": {"title": "1. Приемка новостройки у застройщика", "price": 300, "file": "guides/priemka.pdf"},
    "g2": {"title": "2. Сметный анти-развод (Проверка прораба)", "price": 250, "file": "guides/smeta.pdf"},
    "g3": {"title": "3. Натяжные потолки (Анти-развод)", "price": 200, "file": "guides/potolki.pdf"},
    "g4": {"title": "4. Пластиковые и алюминиевые окна", "price": 200, "file": "guides/okna.pdf"},
    "g5": {"title": "5. Обои и малярка (Брак и контроль)", "price": 150, "file": "guides/oboi.pdf"},
    "g6": {"title": "6. Кафель и плитка (Геометрия, заусовка)", "price": 250, "file": "guides/plitka.pdf"},
    "g7": {"title": "7. Напольные покрытия (Ламинат/Кварцвинил)", "price": 200, "file": "guides/pola.pdf"},
    "g8": {"title": "8. Межкомнатные двери", "price": 200, "file": "guides/dveri.pdf"},
    "g9": {"title": "9. Мягкая мебель (Разоблачение цехов)", "price": 250, "file": "guides/mebel_soft.pdf"},
    "g10": {"title": "10. Корпусная мебель и кухни", "price": 300, "file": "guides/kuhni.pdf"},
    "g11": {"title": "11. Стяжка пола (Технология без трещин)", "price": 200, "file": "guides/styazhka.pdf"},
    "g12": {"title": "12. Сантехника и скрытые работы", "price": 300, "file": "guides/santex.pdf"},
    "g13": {"title": "13. Электрика и щитки", "price": 300, "file": "guides/elektrika.pdf"},
    "g14": {"title": "14. Отопление и теплые полы", "price": 250, "file": "guides/otoplenie.pdf"},
    "g15": {"title": "15. Договоры и работа с бригадами", "price": 250, "file": "guides/dogovor.pdf"},
}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📁 Каталог гайдов (15 тем)", callback_data="catalog")],
        [InlineKeyboardButton("💳 Реквизиты для оплаты", callback_data="pay_info")],
        [InlineKeyboardButton("📞 Поддержка", url="https://t.me/ваш_логин")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Добро пожаловать на портал **Usta.kg**!\n\n"
        "Здесь собраны жесткие практические гайды без воды: честнные расчеты, разоблачения строителей и пошаговые чек-листы.\n\n"
        "Выберите нужный раздел ниже:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "catalog":
        keyboard = []
        for key, guide in GUIDES.items():
            keyboard.append([InlineKeyboardButton(f"{guide['title']} — {guide['price']} сом", callback_data=f"buy_{key}")])
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="main_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("📚 **Выберите нужный гайд для покупки:**", reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == "pay_info":
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="catalog")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "💳 **Способы оплаты:**\n\n"
            "Переведите сумму на карту / кошелек:\n"
            "• **MBank / О!Деньги / DemirBank:** `1234 5678 9012 3456` (Азамат А.)\n\n"
            "После оплаты отправьте сюда скриншот чека, и после проверки вы получите PDF-файл.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif query.data.startswith("buy_"):
        guide_key = query.data.replace("buy_", "")
        guide = GUIDES.get(guide_key)
        context.user_data['selected_guide'] = guide_key

        keyboard = [
            [InlineKeyboardButton("💳 Показать реквизиты", callback_data="pay_info")],
            [InlineKeyboardButton("🔙 К списку гайдов", callback_data="catalog")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"📖 Вы выбрали:\n**{guide['title']}**\n\n"
            f"💰 Стоимость: **{guide['price']} сом**\n\n"
            f"Нажмите кнопку ниже для оплаты, после чего пришлите скриншот чека в этот чат.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("📁 Каталог гайдов (15 тем)", callback_data="catalog")],
            [InlineKeyboardButton("💳 Реквизиты для оплаты", callback_data="pay_info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Главное меню:", reply_markup=reply_markup)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo = update.message.photo[-1].file_id
    
    # Пересылаем чек вам (админу)
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить и выдать гайд", callback_data=f"approve_{user.id}")],
        [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=f"🔔 Новый чек от @{user.username} (ID: {user.id})\nВыбранный гайд: {context.user_data.get('selected_guide', 'Не указан')}",
        reply_markup=reply_markup
    )
    
    await update.message.reply_text("✅ Чек принят! Как только администратор проверит платеж, вам придет PDF-файл.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
