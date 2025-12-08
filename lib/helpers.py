from thefuzz import fuzz


def match_score(text_1: str, text_2: str) -> int:
    return fuzz.partial_ratio(text_1, text_2)
