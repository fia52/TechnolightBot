from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import MessageCantBeEdited, MessageToDeleteNotFound

from loader import db
from tgbot.keyboards.inline import main_menu_keyboard


async def show_main_menu(message):
    if isinstance(message, CallbackQuery):
        data = await db.get_user_by_telegram_id(str(message.from_user.id))
        message = message.message
    else:
        data = await db.get_user_by_telegram_id(str(message.from_user.id))

    try:
        await message.edit_text(
            text=f"""
                ФИО: {data.get("fio")}
Номер телефона: {data.get("phone_number")} 
Должность: {data.get("position")}

Ваш уникальный код: {data.get("unique_code")}            
                """,
        )
        await message.edit_reply_markup(reply_markup=main_menu_keyboard)

    except MessageCantBeEdited:
        await message.answer(
            text=f"""
                ФИО: {data.get("fio")}
Номер телефона: {data.get("phone_number")} 
Должность: {data.get("position")}

Ваш уникальный код: {data.get("unique_code")}            
                """,
            reply_markup=main_menu_keyboard,
        )


async def del_reg_messages(message_ids: list, callback: CallbackQuery):
    for message_id in message_ids:
        try:
            await callback.bot.delete_message(
                chat_id=callback.from_user.id, message_id=message_id
            )
        except MessageToDeleteNotFound:
            pass
