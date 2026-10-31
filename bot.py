import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = "9263148489:AAGL-1gkpgPKbC5yHnG-5Hja3JHcnz4ICWk"
ADMIN_ID = 6930287933

PORT = int(os.environ.get("PORT", 10000))
# Используем ваш актуальный адрес с Render
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://ustakg-bot-1.onrender.com")

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
        [InlineKeyboardButton("💳 QR-код для оплаты", callback_data="pay_info")],
        [InlineKeyboardButton("📞 Поддержка", url="https://t.me/ustakg")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Добро пожаловать на портал **Usta.kg**!\n\n"
        "Здесь собраны жесткие практические гайды без воды: честные расчеты, разоблачения строителей и пошаговые чек-листы.\n\n"
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
        try:
            with open("кюар.jpg", "rb") as photo_file:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=photo_file,
                    caption="💳 **Отсканируйте QR-код для оплаты** через любое банковское приложение (MBank, О!, Demir и др.).\n\nПосле оплаты отправьте скриншот чека ответным сообщением в этот чат.",
                    parse_mode="Markdown"
                )
        except Exception:
            await query.message.reply_text("Не удалось загрузить изображение QR-кода. Убедитесь, что файл 'кюар.jpg' загружен в репозиторий.")

    elif query.data.startswith("buy_"):
        guide_key = query.data.replace("buy_", "")
        guide = GUIDES.get(guide_key)
        context.user_data['selected_guide'] = guide_key

        keyboard = [
            [InlineKeyboardButton("💳 Показать QR-код", callback_data="pay_info")],
            [InlineKeyboardButton("🔙 К списку гайдов", callback_data="catalog")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"📖 Вы выбрали:\n**{guide['title']}**\n\n"
            f"💰 Стоимость: **{guide['price']} сом**\n\n"
            f"Нажмите кнопку ниже для получения QR-кода, после чего пришлите скриншот чека в этот чат.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    elif query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("📁 Каталог гайдов (15 тем)", callback_data="catalog")],
            [InlineKeyboardButton("💳 QR-код для оплаты", callback_data="pay_info")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Главное меню:", reply_markup=reply_markup)

    elif query.data.startswith("approve_"):
        data_parts = query.data.split("_")
        target_user_id = int(data_parts[1])
        guide_key = data_parts[2] if len(data_parts) > 2 else "g1"
        
        guide = GUIDES.get(guide_key, GUIDES["g1"])
        
        try:
            with open(guide["file"], "rb") as f:
                await context.bot.send_document(
                    chat_id=target_user_id,
                    document=f,
                    caption=f"✅ Оплата подтверждена! Вот ваш гайд: **{guide['title']}**",
                    parse_mode="Markdown"
                )
            await query.edit_message_caption(caption=query.message.caption + "\n\n🟢 **ОДОБРЕНО И ВЫДАНО**")
        except Exception as e:
            await query.message.reply_text(f"Ошибка при отправке файла гайда: {e}")

    elif query.data.startswith("reject_"):
        target_user_id = int(query.data.split("_")[1])
        await context.bot.send_message(chat_id=target_user_id, text="❌ К сожалению, ваш платеж отклонен. Если это ошибка, обратитесь в поддержку.")
        await query.edit_message_caption(caption=query.message.caption + "\n\n🔴 **ОТКЛОНЕНО**")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo = update.message.photo[-1].file_id
    selected_guide_key = context.user_data.get('selected_guide', 'g1')
    guide_title = GUIDES.get(selected_guide_key, {}).get('title', 'Гайд')
    
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить и выдать", callback_data=f"approve_{user.id}_{selected_guide_key}")],
        [InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{user.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=f"🔔 Новый чек от @{user.username} (ID: {user.id})\nВыбранный гайд: {guide_title}",
        reply_markup=reply_markup
    )
    
    await update.message.reply_text("✅ Чек принят! Как только администратор проверит платеж, вам автоматически придет PDF-файл.")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    webhook_url = f"{RENDER_URL}/{TOKEN}"
    print(f"Запуск вебхука на URL: {webhook_url}")
    
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()
