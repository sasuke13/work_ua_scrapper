from aiogram import types

from tg_bot.utils import pluralize_year, get_value_of_list


def get_cancel_state_button(text: str, callback_data='CancelState') -> types.InlineKeyboardButton:
    return types.InlineKeyboardButton(text, callback_data=callback_data)


def get_menu_of_platforms():
    return [
        [
            types.InlineKeyboardButton(
                'Work UA',
                callback_data='WorkUA'
            )
        ],
    ]


class WorkUaMenus:
    def get_main_menu(self):
        return [
            [
                types.InlineKeyboardButton(
                    'Вибрати категорії, для пошуку',
                    callback_data='CategoriesWorkUA'
                )
            ],
            [
                types.InlineKeyboardButton(
                    'Ввести ключові слова для сортування користувачів',
                    callback_data='SortByRelevantWordsWorkUA'
                )
            ],
            [
                types.InlineKeyboardButton(
                    'Знайти резюме',
                    callback_data='ParseDataWorkUA'
                )
            ],
            [
                types.InlineKeyboardButton(
                    'Повернутись',
                    callback_data='BackToMainMenu'
                )
            ],
        ]

    def get_menu_for_relevant_words_handler(self):
        return [
            [
                types.InlineKeyboardButton(
                    'Вибрати категорії, для пошуку',
                    callback_data='CategoriesWorkUA'
                )
            ],
            [
                types.InlineKeyboardButton(
                    'Знайти резюме',
                    callback_data='ParseDataWorkUA'
                )
            ],
            [
                get_cancel_state_button('Скасувати ввід')
            ]
        ]

    def get_menu_for_further_search(self):
        return [
            [
                types.InlineKeyboardButton(
                    'Продовжити пошук?',
                    callback_data='ParseDataWorkUA'
                )
            ],

            [
                get_cancel_state_button('Повернутись в головне меню', 'CancelSerch')
            ]
        ]

    def __get_inlinekeyboard_from_category_list(
            self,
            category_list: list,
            key_value: str,
    ) -> list:
        list_of_buttons = []
        temp_row_of_buttons = []
        for option_dict in category_list:
            for key, value in option_dict.items():

                text = key if type(value) != list else value[1]

                if key == 'Вік':
                    text = pluralize_year(value) if value != '0' else 'Будь-який'

                temp_row_of_buttons.append(
                    types.InlineKeyboardButton(
                        text=text,
                        callback_data=f'{key_value}:{get_value_of_list(value, 0)}'
                    )
                )
                if len(temp_row_of_buttons) == 2:
                    list_of_buttons.append(temp_row_of_buttons)
                    temp_row_of_buttons = []

        if len(temp_row_of_buttons):
            list_of_buttons.append(temp_row_of_buttons)
        return list_of_buttons

    def parse_menu_of_categories_and_their_options(self, work_ua_dict_of_categories: dict) -> (list, dict):
        list_of_category_menu = []
        options_dict = {}

        for category, list_of_options in work_ua_dict_of_categories.items():
            list_of_category_menu.append(
                [
                    types.InlineKeyboardButton(
                        category,
                        callback_data=f'{category}:CategoryOption'
                    )
                ]
            )
            options_dict[category] = []
            for option in list_of_options:

                if 'ageto' in option.keys() or 'salaryto' in option.keys():
                    continue

                for tag, options in option.items():
                    list_of_buttons = self.__get_inlinekeyboard_from_category_list(category_list=options, key_value=tag)
                    if len(options_dict[category]):
                        options_dict[category].append(list_of_buttons[0])
                    else:
                        options_dict[category] = list_of_buttons

            options_dict[category].append(
                {
                    types.InlineKeyboardButton(
                        'Повернутись',
                        callback_data='BackToCategoriesWorkUA'
                    )
                }
            )

        list_of_category_menu.append(
            [
                get_cancel_state_button('Скасувати вибірку'),

                types.InlineKeyboardButton(
                    'Повернутись',
                    callback_data='WorkUA'
                )
            ]
        )

        return list_of_category_menu, options_dict


    def get_trimmed_menu(
            self,
            work_ua_dict_of_categories: dict,
            value_to_trim_from: str,
            category: str,
            key_value: str,
    ):
        data = work_ua_dict_of_categories.get(category)[1].get(key_value)

        index = next(index for index, d in enumerate(data) if value_to_trim_from in d[category])

        trimmed_data = data[index + 1:]

        list_of_buttons = self.__get_inlinekeyboard_from_category_list(trimmed_data, key_value)

        list_of_buttons.append(
            [
                types.InlineKeyboardButton(
                    'Не вибрано',
                    callback_data=f'{key_value}:0'
                )
            ],

        )

        list_of_buttons.append(
            [
                get_cancel_state_button('Скасувати вибірку'),

                types.InlineKeyboardButton(
                    'Повернутись',
                    callback_data='BackToCategoriesWorkUA'
                )
            ]
        )

        return list_of_buttons
