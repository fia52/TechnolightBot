import random
import re

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from tgbot.keyboards.inline import main_menu_keyboard, confirm_keyboard, ok_keyboard
from loader import db
from tgbot.keyboards.reply import share_phone_keyboard
from tgbot.misc.help_funcs import show_main_menu, del_reg_messages


class RegistrationFSM(StatesGroup):
    waiting_for_ok_button = State()
    waiting_for_fio = State()
    waiting_for_fio_confirm = State()
    waiting_for_phone_number = State()
    waiting_for_position = State()
    waiting_for_position_confirm = State()


async def start_dialog(message: Message, state: FSMContext):
    if await db.get_user_by_telegram_id(str(message.from_user.id)):
        await show_main_menu(message)
    else:
        await message.answer("Приветственное сообщение", reply_markup=ok_keyboard)
        await message.delete()
        await RegistrationFSM.waiting_for_ok_button.set()


async def obtain_ok_button(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    m2 = await callback.message.edit_text(text="Укажите ваше ФИО:")

    async with state.proxy() as data:
        data["reg_messages_for_delete"] = [
            m2.message_id,
            callback.message.message_id,
        ]

    await RegistrationFSM.waiting_for_fio.set()


async def obtain_fio(message: Message, state: FSMContext):
    fio = message.text
    m3 = await message.answer(text=f"{fio}, вы уверены?", reply_markup=confirm_keyboard)

    async with state.proxy() as data:
        data["fio"] = fio
        data["reg_messages_for_delete"].extend([message.message_id, m3.message_id])

    await RegistrationFSM.waiting_for_fio_confirm.set()


async def obtain_fio_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.data == "yes":
        m4 = await callback.message.answer(
            text="Укажите номер телефона:", reply_markup=share_phone_keyboard
        )

        async with state.proxy() as data:
            data["reg_messages_for_delete"].extend([m4.message_id, callback.message.message_id])

        await RegistrationFSM.waiting_for_phone_number.set()

    else:
        m5 = await callback.message.answer(text="Укажите ваше ФИО:")
        async with state.proxy() as data:
            data["reg_messages_for_delete"].extend([m5.message_id, callback.message.message_id])
        await RegistrationFSM.waiting_for_fio.set()


async def obtain_phone_number(message: Message, state: FSMContext):
    if message.contact:
        async with state.proxy() as data:
            data["phone_number"] = message.contact.phone_number

    else:
        tpl = "^((8|\+7)[\- ]?)(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$"
        if re.match(tpl, message.text):
            async with state.proxy() as data:
                data["phone_number"] = message.text

        else:
            m6 = await message.answer(
                text="Неверный формат номера телефона, попробуйте ещё раз:", reply_markup=share_phone_keyboard
            )
            async with state.proxy() as data:
                data["reg_messages_for_delete"].extend([m6.message_id, message.message_id])
            return

    m7 = await message.answer(
        text="Укажите вашу должность:", reply_markup=ReplyKeyboardRemove()
    )
    async with state.proxy() as data:
        data["reg_messages_for_delete"].extend([m7.message_id, message.message_id])
    await RegistrationFSM.waiting_for_position.set()


async def obtain_position(message: Message, state: FSMContext):
    position = message.text
    m8 = await message.answer(text="вы уверены?", reply_markup=confirm_keyboard)

    async with state.proxy() as data:
        data["position"] = position
        data["reg_messages_for_delete"].extend([message.message_id, m8.message_id])

    await RegistrationFSM.waiting_for_position_confirm.set()


async def obtain_position_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.data == "yes":
        async with state.proxy() as data:
            random.seed(callback.from_user.id)
            random_number = str(random.randint(1, 10000))
            await db.add_user(
                fio=data.get("fio"),
                phone_number=data.get("phone_number"),
                position=data.get("position"),
                unique_code=random_number,
                telegram_id=str(callback.from_user.id),
            )

        m10 = await callback.message.answer(text="Вы успешно прошли регистрацию!")
        await callback.message.answer(
            text=f"""
             ФИО: {data.get("fio")}
Номер телефона: {data.get("phone_number")} 
Должность: {data.get("position")}

Ваш уникальный код: {random_number}            
            """,
            reply_markup=main_menu_keyboard,
        )
        async with state.proxy() as data:
            data["reg_messages_for_delete"].extend([m10.message_id, callback.message.message_id])
        await del_reg_messages(data["reg_messages_for_delete"], callback)
        await state.finish()

    else:
        m9 = await callback.message.answer(text="Укажите вашу должность:")
        async with state.proxy() as data:
            data["reg_messages_for_delete"].extend([m9.message_id, callback.message.message_id])
        await RegistrationFSM.waiting_for_position.set()


def register_registration_handlers(dp: Dispatcher):
    dp.register_message_handler(start_dialog, commands=["start"], state="*"),
    dp.register_callback_query_handler(
        show_main_menu,
        lambda x: x.data and x.data == "main_menu",
        state="*",
    ),
    dp.register_callback_query_handler(
        obtain_ok_button,
        lambda x: x.data and x.data == "ok",
        state=RegistrationFSM.waiting_for_ok_button,
    ),
    dp.register_message_handler(
        obtain_fio, content_types=["text"], state=RegistrationFSM.waiting_for_fio
    ),
    dp.register_callback_query_handler(
        obtain_fio_confirm,
        lambda x: x.data and x.data in ["yes", "change"],
        state=RegistrationFSM.waiting_for_fio_confirm,
    ),
    dp.register_message_handler(
        obtain_phone_number,
        content_types=["contact", "text"],
        state=RegistrationFSM.waiting_for_phone_number,
    ),
    dp.register_message_handler(
        obtain_position,
        content_types=["text"],
        state=RegistrationFSM.waiting_for_position,
    ),
    dp.register_callback_query_handler(
        obtain_position_confirm,
        lambda x: x.data and x.data in ["yes", "change"],
        state=RegistrationFSM.waiting_for_position_confirm,
    )
