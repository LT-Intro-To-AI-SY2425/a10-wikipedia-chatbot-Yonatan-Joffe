#me and andrew
import re, string
from wikipedia import WikipediaPage
import wikipedia
from bs4 import BeautifulSoup
from match import match
from typing import List, Callable, Tuple, Any, Match

def get_page_html(title: str) -> str:
    results = wikipedia.search(title)
    return WikipediaPage(results[0]).html()


def get_first_infobox_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all(class_="infobox")

    if not results:
        raise LookupError("Page has no infobox")
    return results[0].text


def clean_text(text: str) -> str:
    only_ascii = "".join([char if char in string.printable else " " for char in text])
    no_dup_spaces = re.sub(" +", " ", only_ascii)
    no_dup_newlines = re.sub("\n+", "\n", no_dup_spaces)
    return no_dup_newlines


def get_match(
    text: str,
    pattern: str,
    error_text: str = "Page doesn't appear to have the property you're expecting",
) -> Match:
    p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
    match = p.search(text)
    if not match:
        raise AttributeError(error_text)
    return match


def get_capital_city(capital_name: str) -> str:
    """Gets the capital city of a country

    Args:
        country_name - name of the country

    Returns:
        capital city of the country
    """
    infobox_text = clean_text(get_first_infobox_text(get_page_html(capital_name)))
    # Updated regex pattern to be more flexible
    pattern = r"(?:capital[^\w]*[:|]?[^\w]*)(?P<capital>[A-Za-z\s]+)"
    error_text = "Page infobox has no capital city information"
    match = get_match(infobox_text, pattern, error_text)

    capital_city = match.group("capital")

    if "and largest city" in capital_city:
        capital_city = capital_city.replace("and largest city", "").strip()

    return capital_city



def get_population(country_name: str) -> str:
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country_name)))
    pattern = r"Population(?:[^0-9]{0,20})?.*?(?P<pop>[0-9][0-9, ]{6,})"
    error_text = "Page infobox has no population information"
    match = get_match(infobox_text, pattern, error_text)
    return match.group("pop").strip()


def get_official_language(country_name: str) -> str:
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country_name)))
    pattern = r"Official language[\s]?(?:\(.*?\))?\s*(?P<lang>[A-Za-z, \[\]]+)"
    error_text = "Page infobox has no official language information"
    match = get_match(infobox_text, pattern, error_text)
    return match.group("lang").strip()


def capital_city(matches: List[str]) -> List[str]:
    return [get_capital_city(" ".join(matches))]


def population(matches: List[str]) -> List[str]:
    return [get_population(" ".join(matches))]


def official_language(matches: List[str]) -> List[str]:
    return [get_official_language(" ".join(matches))]


def bye_action(dummy: List[str]) -> None:
    raise KeyboardInterrupt


Pattern = List[str]
Action = Callable[[List[str]], List[Any]]

pa_list: List[Tuple[Pattern, Action]] = [
    ("what is the capital of %".split(), capital_city),
    ("what is the population of %".split(), population),
    ("what is the official language of %".split(), official_language),
    (["bye"], bye_action),
]


def search_pa_list(src: List[str]) -> List[str]:
    for pat, act in pa_list:
        mat = match(pat, src)
        if mat is not None:
            answer = act(mat)
            return answer if answer else ["No answers"]
    return ["I don't understand"]


def query_loop() -> None:
    print("Welcome to the Wikipedia chatbot!\n")
    while True:
        try:
            print()
            query = input("Your query? ").replace("?", "").lower().split()
            answers = search_pa_list(query)
            for ans in answers:
                print(ans)
        except (KeyboardInterrupt, EOFError):
            break

    print("\nSo long!\n")


query_loop()
