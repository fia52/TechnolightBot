from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import db
from tgbot.keyboards.callback_datas import pagination_call, event_call

main_menu_keyboard = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Знакомства", callback_data="acquaintance"),
            InlineKeyboardButton(text="Расписание", callback_data="schedule"),
        ],
        [
            InlineKeyboardButton(text="Карта", callback_data="map"),
            InlineKeyboardButton(text="FAQ", switch_inline_query_current_chat="faq"),
        ],
    ],
)

confirm_keyboard = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="yes"),
            InlineKeyboardButton(text="Изменить", callback_data="change"),
        ]
    ],
)

acquaintance_keyboard = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Указать код", callback_data="enter_code"),
            InlineKeyboardButton(text="История поиска", callback_data="search_history"),
        ],
        [InlineKeyboardButton(text="Назад", callback_data="main_menu")],
    ],
)

schedule_keyboard = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Кулинарный батл",
                callback_data=event_call.new(title="culinary_battle"),
            )
        ],
        [
            InlineKeyboardButton(
                text="Большие гонки", callback_data=event_call.new(title="big_races")
            )
        ],
        [
            InlineKeyboardButton(
                text="Битва умов", callback_data=event_call.new(title="battle_of_wits")
            )
        ],
        [
            InlineKeyboardButton(
                text="Дневной дозор", callback_data=event_call.new(title="day_watch")
            )
        ],
        [InlineKeyboardButton(text="Назад", callback_data="main_menu")],
    ],
)

record_keyboard = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Записаться", callback_data="record"),
        ],
        [InlineKeyboardButton(text="Назад", callback_data="schedule")],
    ],
)

confirm_record_keyboard = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="yes"),
            InlineKeyboardButton(text="Нет", callback_data="no"),
        ]
    ],
)

ok_keyboard = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Окей", callback_data="ok"),
        ]
    ],
)

go_back_keyboard = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="acquaintance")],
    ],
)


async def get_users_keyboard(
    user_codes: list,
    num: int = 0,
):
    user_code = user_codes[num]
    user = await db.get_user_by_code(code=user_code)

    pages_buttons = list()

    previous_num = num - 1
    previous_num_text = "<< "

    next_num = num + 1
    next_num_text = " >>"

    if previous_num >= 0:
        pages_buttons.append(
            InlineKeyboardButton(
                text=previous_num_text,
                callback_data=pagination_call.new(num=previous_num),
            )
        )
    else:
        pages_buttons.append(
            InlineKeyboardButton(
                text=" . ",
                callback_data=pagination_call.new(num="empty"),
            )
        )

    if next_num <= len(user_codes) - 1:
        pages_buttons.append(
            InlineKeyboardButton(
                text=next_num_text,
                callback_data=pagination_call.new(num=next_num),
            )
        )
    else:
        pages_buttons.append(
            InlineKeyboardButton(
                text=" . ",
                callback_data=pagination_call.new(num="empty"),
            )
        )

    markup = InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[
            pages_buttons,
            [InlineKeyboardButton(text="Назад", callback_data="acquaintance")],
        ],
    )

    return user, markup
