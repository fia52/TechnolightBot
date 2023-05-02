from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from tgbot.keyboards.inline import go_back_to_main_menu_keyboard


async def show_map(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    with open(f"tgbot/data/map.png", "rb") as f:
        await callback.bot.send_photo(
            chat_id=callback.from_user.id,
            photo=f,
            reply_markup=go_back_to_main_menu_keyboard,
        )

    await callback.bot.delete_message(
        chat_id=callback.from_user.id, message_id=callback.message.message_id
    )


def register_map_handlers(dp):
    dp.register_callback_query_handler(
        show_map, lambda x: x.data and x.data == "map", state="*"
    ),
