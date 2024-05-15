from srcapper.relevant_keywords_module import SortDictByRelevantWords
from srcapper.work_ua.work_ua_webscrapper import (
    generate_link_with_filters,
    parse_resumes_list_by_filters,
    get_organized_list_of_candidates, parse_categories_and_get_categories_dict
)


async def parse_organized_data_with_categories(additional_keywords: list | None = None, *args, **kwargs) -> list:
    additional_keywords = additional_keywords if additional_keywords else []
    link = generate_link_with_filters(*args, **kwargs)
    candidates = await parse_resumes_list_by_filters(search_engine_str=link)
    candidates = get_organized_list_of_candidates(candidates)
    candidates = SortDictByRelevantWords().get_sorted_dict_by_relevant_keywords(candidates, additional_keywords)
    return candidates


async def get_filters_dict() -> dict:
    return await parse_categories_and_get_categories_dict()
