from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


share_phone_keyboard = ReplyKeyboardMarkup(
    row_width=1, resize_keyboard=True, one_time_keyboard=True
)
share_phone_keyboard.add(
    KeyboardButton(text="Поделиться номером телефона", request_contact=True)
)
