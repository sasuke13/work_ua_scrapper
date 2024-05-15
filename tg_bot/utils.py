import re


def split_callback_data_and_get_value(callback_data: str, delimiter: str, index: int) -> str:
    split_data = callback_data.split(delimiter)

    return split_data[index]


def pluralize_year(number):
    if re.match(r'.*1$', number):
        return f'{number} рік'
    elif re.match(r'.*[2-4]$', number) and not re.match(r'14', number):
        return f'{number} роки'
    else:
        return f'{number} років'


def get_value_of_list(value: str | list, index: int):
    return value[index] if type(value) == list else value
