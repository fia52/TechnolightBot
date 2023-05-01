from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.utils.exceptions import MessageToDeleteNotFound

from tgbot.data.events_info_dict import events_info_dict
from tgbot.keyboards.callback_datas import event_call
from tgbot.keyboards.inline import (
    schedule_keyboard,
    record_keyboard,
    confirm_record_keyboard,
)
from loader import googledocred, db


class EventRecordFSM(StatesGroup):
    waiting_for_event_title = State()
    waiting_for_record_request = State()
    waiting_for_record_confirm = State()


async def schedule_show(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    current_state = await state.get_state()
    if current_state is not None:
        async with state.proxy() as data:
            try:
                await callback.bot.delete_message(
                    chat_id=callback.from_user.id,
                    message_id=data["message_for_delete_id"],
                )
            except (MessageToDeleteNotFound, KeyError):
                pass
        await state.finish()

    message = await callback.message.answer(
        text="Информация по событиям:", reply_markup=schedule_keyboard
    )
    await callback.bot.delete_message(
        chat_id=callback.from_user.id, message_id=callback.message.message_id
    )

    async with state.proxy() as data:
        data["message_for_redact_id"] = message.message_id

    await EventRecordFSM.waiting_for_event_title.set()


async def event_info(callback: CallbackQuery, callback_data: dict, state: FSMContext):
    await callback.answer()

    event_title = callback_data.get("title")
    async with state.proxy() as data:
        data["event_title"] = event_title

    event_text = events_info_dict.get(event_title)

    with open(f"tgbot/data/{event_title}.png", "rb") as f:
        await callback.bot.send_photo(
            chat_id=callback.from_user.id,
            photo=f,
            caption=event_text,
            reply_markup=record_keyboard,
        )

        await callback.bot.delete_message(
            chat_id=callback.from_user.id, message_id=callback.message.message_id
        )

    await EventRecordFSM.waiting_for_record_request.set()


async def obtain_record_request(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    async with state.proxy() as data:
        data["event_name"] = {
            "culinary_battle": "Кулинарный батл",
            "big_races": "Большие гонки",
            "battle_of_wits": "Битва умов",
            "day_watch": "Дневной дозор",
        }.get(data["event_title"])

        await callback.message.answer(
            text=f"Подтверждаете запись на «{data['event_name']}» ?",
            reply_markup=confirm_record_keyboard,
        )
        await callback.bot.delete_message(
            chat_id=callback.from_user.id, message_id=callback.message.message_id
        )

    await EventRecordFSM.waiting_for_record_confirm.set()


async def obtain_record_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    async with state.proxy() as data:
        if callback.data == "yes":
            await callback.message.answer(
                text=f"Вы успешно записались на мероприятие «{data['event_name']}»"
            )

            user = await db.get_user_by_telegram_id(str(callback.from_user.id))
            await googledocred.add_record_to_table(
                values=[
                    user.get("fio"),
                    user.get("position"),
                    user.get("phone_number"),
                    user.get("unique_code"),
                ],
                event_name=data["event_name"],
            )

        await schedule_show(callback, state)


def register_schedule_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        schedule_show, lambda x: x.data and x.data == "schedule", state="*"
    ),
    dp.register_callback_query_handler(
        event_info, event_call.filter(), state=EventRecordFSM.waiting_for_event_title
    ),
    dp.register_callback_query_handler(
        obtain_record_request,
        lambda x: x.data and x.data == "record",
        state=EventRecordFSM.waiting_for_record_request,
    ),
    dp.register_callback_query_handler(
        obtain_record_confirm,
        lambda x: x.data and x.data in ["yes", "no"],
        state=EventRecordFSM.waiting_for_record_confirm,
    )
