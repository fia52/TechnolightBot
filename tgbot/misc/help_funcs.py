from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import MessageCantBeEdited, MessageToDeleteNotFound, BadRequest

from loader import db
from tgbot.keyboards.inline import main_menu_keyboard


async def show_main_menu(message, method: str = "try_to_edit_previous_message"):
    if isinstance(message, CallbackQuery):
        await message.answer()
        data = await db.get_user_by_telegram_id(str(message.from_user.id))
        message_convert = message.message
    else:
        message_convert = message
        data = await db.get_user_by_telegram_id(str(message.from_user.id))

    if method == "delete_previous_message":
        await message_convert.answer(
            text=f"""
                ФИО: {data.get("fio")}
Номер телефона: {data.get("phone_number")} 
Должность: {data.get("position")}

Ваш уникальный код: {data.get("unique_code")}            
            """,
            reply_markup=main_menu_keyboard,
        )
        await message.bot.delete_message(chat_id=message.from_user.id, message_id=message_convert.message_id)
        return

    try:
        await message_convert.edit_text(
            text=f"""
                ФИО: {data.get("fio")}
Номер телефона: {data.get("phone_number")} 
Должность: {data.get("position")}

Ваш уникальный код: {data.get("unique_code")}            
                """,
        )
        await message_convert.edit_reply_markup(reply_markup=main_menu_keyboard)

    except (MessageCantBeEdited, BadRequest,):
        await message_convert.answer(
            text=f"""
                ФИО: {data.get("fio")}
Номер телефона: {data.get("phone_number")} 
Должность: {data.get("position")}

Ваш уникальный код: {data.get("unique_code")}            
                """,
            reply_markup=main_menu_keyboard,
        )
        try:
            await message.bot.delete_message(chat_id=message_convert.from_user.id, message_id=message.message_id)
        except AttributeError:
            await message.bot.delete_message(chat_id=message.from_user.id, message_id=message_convert.message_id)


async def del_reg_messages(message_ids: list, callback: CallbackQuery):
    for message_id in message_ids:
        try:
            await callback.bot.delete_message(
                chat_id=callback.from_user.id, message_id=message_id
            )
        except MessageToDeleteNotFound:
            pass
