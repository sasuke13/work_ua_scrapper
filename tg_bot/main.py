import asyncio
import os
import re

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

from aiogram import Bot
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor

import io
import json
from aiogram import types

from tg_bot.menus import WorkUaMenus, get_menu_of_platforms
from srcapper.work_ua import work_ua_interactors
from tg_bot.states import WorkUAState
from tg_bot.utils import split_callback_data_and_get_value

load_dotenv()

bot = Bot(os.environ.get('TELEGRAM_BOT_KEY'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

work_ua_list_of_categories = []


async def change_last_message_with_inline_keyboard(callback_query, text_to_change, inline_keyboard):
    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=text_to_change,
    )

    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=inline_keyboard
    )


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=get_menu_of_platforms())
    await bot.send_message(
        message.from_user.id,
        f'Привіт, з якої платформи ви хочете отримати данні про кандидатів?',
        reply_markup=inline_keyboard
    )


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'CancelState', state='*')
async def cancel_state_handler(callback_query: types.CallbackQuery, state: FSMContext):
    if state:
        await state.finish()

    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=get_menu_of_platforms())

    text = 'Привіт, з якої платформи ви хочете отримати данні про кандидатів?'

    await change_last_message_with_inline_keyboard(callback_query, text, inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'CancelSerch', state='*')
async def cancel_search_handler(callback_query: types.CallbackQuery, state: FSMContext):
    if state:
        await state.finish()

    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=get_menu_of_platforms())
    await bot.send_message(
        callback_query.from_user.id,
        f'Привіт, з якої платформи ви хочете отримати данні про кандидатів?',
        reply_markup=inline_keyboard
    )


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'WorkUA', state='*')
async def work_ua_menu(callback_query: types.CallbackQuery):
    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=WorkUaMenus().get_main_menu())
    text = 'Виберіть опції пошуку кандидатів:'

    await change_last_message_with_inline_keyboard(callback_query, text, inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'BackToMainMenu')
async def back_to_main_menu(callback_query: types.CallbackQuery):
    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=get_menu_of_platforms())
    text = 'Привіт, з якої платформи ви хочете отримати данні про кандидатів?',

    await change_last_message_with_inline_keyboard(callback_query, text, inline_keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'ParseDataWorkUA', state='*')
async def parse_data_work_ua(callback_query: types.CallbackQuery, state: FSMContext):
    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=WorkUaMenus().get_menu_for_further_search())

    state_data = await state.get_data()
    print(state_data)
    page = state_data.get('page', 1)
    relevant_words = state_data.get('relevant_words', [])
    categories = state_data.get('categories', {})
    categories['page'] = str(page)

    data = await work_ua_interactors.parse_organized_data_with_categories(relevant_words, **categories)

    json_data = json.dumps(data, ensure_ascii=False, indent=4).encode('utf-8')

    file_obj = io.BytesIO(json_data)

    await callback_query.message.answer_document(document=file_obj, reply_markup=inline_keyboard)

    await state.update_data({'page': page + 1})


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'SortByRelevantWordsWorkUA', state='*')
async def sort_by_relevant_words_workua(callback_query: types.CallbackQuery):
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text="Введіть ключові слова для сортування користувачів:"
    )

    await WorkUAState.WaitingForInput.set()


@dp.message_handler(state=WorkUAState.WaitingForInput)
async def relevant_words_handler(message: types.Message, state: FSMContext):
    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=WorkUaMenus().get_menu_for_relevant_words_handler())

    if re.fullmatch(r'^(\w+)(,\s\w+)*$', message.text):
        relevant_words = message.text.split(', ')
        await state.update_data({'relevant_words': relevant_words})
        await bot.send_message(
            message.from_user.id,
            f'Данні успішно збережено!',
            reply_markup=inline_keyboard
        )

    else:
        await message.reply(
            "Данні введені не правильно!\n\n"
            "Правильний формат "
            "вводу данних повинен виглядати ось так: "
            "(Параметр1, параметр2..., або єдиний_параметр)",
            reply_markup=inline_keyboard
        )


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'BackToCategoriesWorkUA', state='*')
async def back_to_categories_work_ua_handler(callback_query: types.CallbackQuery, state: FSMContext):
    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=list_of_category_menu)
    text = 'Виберіть потрібні категорії:'

    await change_last_message_with_inline_keyboard(callback_query, text, inline_keyboard)


@dp.callback_query_handler(
    lambda callback_query:
        callback_query.data == 'CategoriesWorkUA' or
        callback_query.data == 'BackToCategoriesWorkUA',
    state='*'
)
async def categories_work_ua_handler(callback_query: types.CallbackQuery, state: FSMContext):
    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=list_of_category_menu)
    text = 'Виберіть потрібні категорії:'

    await change_last_message_with_inline_keyboard(callback_query, text, inline_keyboard)

    await WorkUAState.Categories.set()


@dp.callback_query_handler(lambda callback_query: 'CategoryOption' in callback_query.data, state='*')
async def category_options_work_ua_handler(callback_query: types.CallbackQuery, state: FSMContext):
    data = split_callback_data_and_get_value(callback_query.data, ':', 0)

    inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=options_dict[data])

    await bot.edit_message_reply_markup(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        reply_markup=inline_keyboard
    )


@dp.callback_query_handler(lambda callback_query: ':' in callback_query.data, state='*')
async def save_category_to_state_work_ua_handler(callback_query: types.CallbackQuery, state: FSMContext):
    split_callback_query_data = callback_query.data.split(':')
    state_data = await state.get_data()
    picked_data = state_data.get('categories', {})

    key = split_callback_query_data[0]
    value = split_callback_query_data[1]

    if (key in picked_data) and ('age' not in key and 'salary' not in key):
        picked_data[key].append(value)
    else:
        picked_data[key] = [value]

    await state.update_data({'categories': picked_data})

    if key == 'agefrom':
        text = 'Виберіть крайній вік кандидата:'

        inline_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=WorkUaMenus().get_trimmed_menu(
                work_ua_dict_of_categories=work_ua_dict_of_categories,
                value_to_trim_from=value,
                category='Вік',
                key_value='ageto'
            )
        )

    elif key == 'salaryfrom':
        text = 'Виберіть крайнє зарплатне очікування кандидата:'

        inline_keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=WorkUaMenus().get_trimmed_menu(
                work_ua_dict_of_categories=work_ua_dict_of_categories,
                value_to_trim_from=value,
                category='Зарплата',
                key_value='salaryto',
            )
        )

    else:
        inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=list_of_category_menu)
        text = 'Виберіть потрібні категорії:'

    await change_last_message_with_inline_keyboard(callback_query, text, inline_keyboard)


if __name__ == "__main__":
    work_ua_dict_of_categories = asyncio.run(work_ua_interactors.get_filters_dict())
    list_of_category_menu, options_dict = (WorkUaMenus().
                                           parse_menu_of_categories_and_their_options(work_ua_dict_of_categories))
    executor.start_polling(dp)
