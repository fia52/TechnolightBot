from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from loader import db
from tgbot.keyboards.callback_datas import pagination_call
from tgbot.keyboards.inline import acquaintance_keyboard, get_users_keyboard, go_back_to_acquaintance_menu_keyboard


class SearchByCodeFSM(StatesGroup):
    waiting_for_enter_code_button = State()
    waiting_for_code = State()


async def acquaintance_menu_show(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await db.get_user_by_telegram_id(str(callback.from_user.id))
    await callback.message.edit_text(
        text=f"""
                ФИО: {data.get("fio")}
Номер телефона: {data.get("phone_number")} 
Должность: {data.get("position")}

Ваш уникальный код: {data.get("unique_code")}            
        """,
    )

    await callback.message.edit_reply_markup(reply_markup=acquaintance_keyboard)
    await SearchByCodeFSM.waiting_for_enter_code_button.set()


async def enter_code_dialog(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    message_ = await callback.message.edit_text(text="Укажите код", reply_markup=go_back_to_acquaintance_menu_keyboard)

    async with state.proxy() as data:
        data["message_for_redact_id"] = message_.message_id
    await SearchByCodeFSM.waiting_for_code.set()


async def show_user_info_by_code(message: Message, state: FSMContext):
    code = message.text
    async with state.proxy() as data:
        message_for_redact_id = data["message_for_redact_id"]

    user_info = await db.get_user_by_code(code)
    if user_info:
        await message.bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=message_for_redact_id,
            text=f"""
ФИО: {user_info.get("fio")}
Номер телефона: {user_info.get("phone_number")} 
Должность: {user_info.get("position")}

Уникальный код: {code}            
        """
        )
        await message.bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=message_for_redact_id,
            reply_markup=go_back_to_acquaintance_menu_keyboard
        )
        await db.add_to_search_history(telegram_id=str(message.from_user.id), code=code)

    else:
        await message.bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=message_for_redact_id,
            text="Пользователя с таким кодом не найдено"
        )
        await message.bot.edit_message_reply_markup(
            chat_id=message.from_user.id,
            message_id=message_for_redact_id,
            reply_markup=go_back_to_acquaintance_menu_keyboard
        )

    await message.delete()
    await SearchByCodeFSM.waiting_for_enter_code_button.set()


async def show_search_history(callback: CallbackQuery, state: FSMContext):
    history = await db.get_search_history(telegram_id=str(callback.from_user.id))
    if len(history) == 0:
        await callback.message.edit_text(
            text="История поиска пуста", reply_markup=acquaintance_keyboard
        )
    else:
        user, markup = await get_users_keyboard(user_codes=history)

        await callback.message.edit_text(
            text=f"""
            ФИО: {user.get("fio")}
Номер телефона: {user.get("phone_number")} 
Должность: {user.get("position")}

Уникальный код: {user.get("unique_code")}            
        """,
        )

        await callback.message.edit_reply_markup(markup)


async def show_chosen_user(callback: CallbackQuery, callback_data: dict):
    await callback.answer()

    if callback_data.get("num") == "empty":
        return

    current_num = int(callback_data.get("num"))
    history = await db.get_search_history(telegram_id=str(callback.from_user.id))
    user, markup = await get_users_keyboard(user_codes=history, num=current_num)
    await callback.message.edit_text(
        text=f"""
        ФИО: {user.get("fio")}
Номер телефона: {user.get("phone_number")} 
Должность: {user.get("position")}
        
Уникальный код: {user.get("unique_code")}            
        """,
    )

    await callback.message.edit_reply_markup(markup)


def register_acquaintance_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        acquaintance_menu_show, lambda x: x.data and x.data == "acquaintance", state="*"
    ),
    dp.register_callback_query_handler(
        enter_code_dialog,
        lambda x: x.data and x.data == "enter_code",
        state=SearchByCodeFSM.waiting_for_enter_code_button,
    ),
    dp.register_message_handler(
        show_user_info_by_code,
        content_types=["text"],
        state=SearchByCodeFSM.waiting_for_code,
    ),
    dp.register_callback_query_handler(
        show_search_history, lambda x: x.data and x.data == "search_history", state="*"
    ),
    dp.register_callback_query_handler(
        show_chosen_user, pagination_call.filter(), state="*"
    )
