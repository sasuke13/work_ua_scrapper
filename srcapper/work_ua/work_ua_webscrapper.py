import asyncio

import re
from collections import OrderedDict

from bs4 import BeautifulSoup

from srcapper.base_methods import get_site_content, get_bs4_instance
from srcapper.relevant_keywords_module import SortDictByRelevantWords

MAIN_PAGE = 'https://www.work.ua/resumes/?page=1'  # page to get categories


def get_next_or_previous_element_from_tag(tag: BeautifulSoup, element: str) -> BeautifulSoup | None:
    next_element = tag.find_next(element)
    previous_element = tag.find_previous(element)

    return previous_element if previous_element else next_element if next_element else None


def get_dict_for_category(selection, targets) -> dict:
    targets_list = []

    for target in targets:
        label = get_next_or_previous_element_from_tag(target, 'label')
        clear_label = re.sub(r'\d+(\s\d+)*$', '', label.text.strip())
        value = target['value'] if target.get('value') else ''

        if clear_label == 'Зарплата':
            text = re.sub(r'\((\d+)\)', '', target.text).strip()
            value = [value, text]

        targets_list.append({clear_label: value})

    selection_dict = {
        selection['id'].split('_')[0]:
            targets_list
    }

    return selection_dict



async def parse_categories_and_get_categories_dict() -> dict:
    categories_dict = {}

    sites_soup = await get_site_content(MAIN_PAGE)

    form_groups = sites_soup.find_all('div', class_='form-group')

    for item in form_groups:
        category = get_bs4_instance(str(item))
        selections = category.find_all(re.compile(r'(div|select)'), {'id': re.compile(r'\b\w+_selection\b')})
        label = category.find('label')
        label = label.get_text() if label else ''

        if selections:
            for selection in selections:
                if label not in categories_dict:
                    categories_dict[label] = []
                options = selection.find_all('option')
                inputs = selection.find_all('input')

                gathered_options = options + inputs

                temp_selection_dict = get_dict_for_category(selection, gathered_options)
                categories_dict[label].append(temp_selection_dict)

    return categories_dict


def generate_link_with_filters(**kwargs) -> str:
    search_engine_str = 'https://www.work.ua/resumes/?'
    for key, value in kwargs.items():
        search_engine_str += f'{key}='
        for list_item in value:
            search_engine_str += f'{list_item}'
            if list_item != value[-1]:
                search_engine_str += '+'
            else:
                search_engine_str += '&'

    return search_engine_str


async def parse_resumes_list_by_filters(search_engine_str):
    sites_soup = await get_site_content(search_engine_str)

    anchors = sites_soup.find_all('a', {'name': re.compile(r'\d+')})
    link_url = 'https://www.work.ua/resumes/'

    candidates_links = [link_url + anchor['name'] + '/' for anchor in anchors if anchor.get('name')]

    list_of_coroutines = await asyncio.gather(*[get_site_content(link) for link in candidates_links])

    parsed_candidates = []
    for r in list_of_coroutines:
        d = r.find('div', {'class': 'card wordwrap cut-top'})
        text = d.find_all(re.compile(r'(h1|h2|p|span|dt|dd)'))
        parsed_candidates.append(text)

    return parsed_candidates


def get_organized_list_of_candidates(candidates) -> list:
    list_of_candidates = []

    for candidate in candidates:
        elems = list(OrderedDict.fromkeys([t.text.replace('\n', '').strip() for t in candidate if t != '']))
        elems = [re.sub(r'\s+', ' ', t) for t in elems]

        list_of_candidates.append(elems)

    return list_of_candidates


if __name__ == '__main__':
    asyncio.run(parse_categories_and_get_categories_dict())
    link = generate_link_with_filters(category=['1'], agefrom=['16'], ageto=['25'])
    print(link)
    loop = asyncio.get_event_loop()
    candidates = loop.run_until_complete(parse_resumes_list_by_filters(link))
    candidates = get_organized_list_of_candidates(candidates)
    print(candidates)
    print(SortDictByRelevantWords().get_sorted_dict_by_relevant_keywords(candidates, ['HTML']))
