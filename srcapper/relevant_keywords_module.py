class SortDictByRelevantWords:
    __LIST_OF_HELPFUL_KEYWORDS = [
        'Освіта',
        'Досвід роботи',
        'Додаткова інформація',
        'Знання і навички',
        'Знання мов',
        'Завантажений файл'
    ]

    def get_sorted_dict_by_relevant_keywords(
            self,
            candidates: list[list[str]],
            additional_keywords: list[str] | None = None
    ) -> list[list[str]]:
        relevant_words = self.__LIST_OF_HELPFUL_KEYWORDS + additional_keywords \
                         if additional_keywords else self.__LIST_OF_HELPFUL_KEYWORDS


        for candidate in candidates:

            relevant_words_of_the_candidate = [word for word in relevant_words if word in candidate]

            message = ('У цього кандидата є збіги по релевантних словах (' +
                       str(relevant_words_of_the_candidate)[1:-1] + ')')
            candidate.append(message)
            candidate.append(len(relevant_words_of_the_candidate))

        return sorted(candidates, key=lambda candidate: candidate[-1], reverse=True)
