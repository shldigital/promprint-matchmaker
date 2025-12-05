"""Functions to manage search using typesense server."""
import pandas as pd
import typesense


def search(
        text: str,
        collection_name: str,
        client: typesense.Client
) -> dict:
    """
    Perform a query on the passed typesense client

    :param text: Text to search for in the typsense collection
    :type text: str
    :param collection_name: Name of the typesense collection to search inside
    :type collection_name: str
    :param client: Initialised typesense client providing connection to server
    :type client: typesense.Client
    :return: Query response info
    :rtype: dict
    """
    search_params = {
        'q': text,
        'query_by': 'title',
        'pre_segemented_query': True,
        'num_typos': 2,
        'min_len_1typo': 4,
        'min_len_2typo': 7,
        'split_join_tokens': 'fallback',
        'typo_tokens_threshold': 1,
        'drop_tokens_threshold': 1,
        'drop_tokens_mode': 'left_to_right',
        'prioritize_exact_match': True,
        'prioritize_token_position': False,
    }
    return (client.collections[collection_name].documents
            .search(search_params))


def make_query_subset(
        text: str,
        collection_name: str,
        drop_token_filter: int,
        client: typesense.Client
) -> pd.DataFrame:
    """
    Returns a dataframe populated with typesense search hits.

    :param text: Text to search for in the typsense collection
    :type text: str
    :param collection_name: Name of the typesense collection to search inside
    :type collection_name: str
    :param drop_token_filter: Remove hits that dropped this many tokens or more
    :type drop_token_filter: int
    :param client: Initialised typesense client providing connection to server
    :type client: typesense.Client
    :return: Query response info
    :rtype: dict
    """
    collection = pd.DataFrame(columns=["id"])
    response = search(text, collection_name, client)
    if response["found"] > 0:
        collection_dict = {
            "id": map(lambda h: h["document"]["id"], response["hits"]),
            "clean_title": map(lambda h: h["document"]["title"], response["hits"]),
            "typesense_score": map(lambda h: h["text_match_info"]["score"], response["hits"]),
            "num_tokens_dropped": map(lambda h: h["text_match_info"]["num_tokens_dropped"], response["hits"]),
            "tokens_matched": map(lambda h: h["text_match_info"]["tokens_matched"], response["hits"]),
            "typo_prefix_score": map(lambda h: h["text_match_info"]["typo_prefix_score"], response["hits"])
        }
        collection = pd.DataFrame(data=collection_dict)
        collection = collection[collection["num_tokens_dropped"] < drop_token_filter]
    return collection.set_index("id")
