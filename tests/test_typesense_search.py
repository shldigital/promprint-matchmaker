import os
import pandas as pd
import pytest
import typesense

from dotenv import load_dotenv
from pathlib import Path
from lib.typesense_search import search, make_query_subset


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load env variables from .env file if defined
env_path = BASE_DIR / ".env"
load_dotenv(env_path, override=True)

test_docs_path = BASE_DIR / "tests/test_files/test_docs.tsv"


@pytest.fixture(scope="module")
def typesense_client():
    API_KEY = os.environ.get('TYPESENSE_KEY', '')
    HOSTNAME = os.environ.get('TYPESENSE_HOST', '')
    PORT = os.environ.get('TYPESENSE_PORT', '')
    client = typesense.Client({
        'api_key': API_KEY,
        'nodes': [{
            'host': HOSTNAME,
            'port': PORT,
            'protocol': 'http'
        }],
        'connection_timeout_seconds': 2
    })
    return client


@pytest.fixture(scope="module")
def test_collection(typesense_client):
    response = typesense_client.collections.create({
        "name": "test",
        "fields": [
                {"name": "title", "type": "string"},
                {"name": "id", "type": "string"}
            ]
        })
    yield response
    typesense_client.collections['test'].delete()


@pytest.fixture(scope="module")
def test_documents(typesense_client, test_collection):
    collection_name = test_collection["name"]
    df = pd.read_csv(test_docs_path, sep='\t')
    df = pd.concat([df["id"], df["clean_title"]], axis=1)
    df.rename(columns={"clean_title": "title"}, inplace=True)
    entries = df.to_dict('records')
    response = (typesense_client.collections[collection_name].documents
                .import_(entries, {'action': 'create'}))
    return response


def test_mock_collection_created(typesense_client, test_collection, test_documents):
    collection_name = test_collection["name"]
    collection = typesense_client.collections[collection_name].retrieve()
    num_documents = collection["num_documents"]

    df = pd.read_csv(test_docs_path, sep='\t')
    successes = map(lambda r: r["success"], test_documents)

    assert all(successes) and num_documents == df.shape[0]


def test_search_full_title_hit(typesense_client, test_collection, test_documents):
    title = "gods glory in the heavens"
    collection = test_collection["name"]
    response = search(title, collection, typesense_client)
    assert response["found"] == 1 and response["hits"][0]["document"]["title"] == title


def test_query_subset_single_find(typesense_client, test_collection, test_documents):
    title = "gods glory in the heavens"
    collection_name = test_collection["name"]
    collection = make_query_subset(title, collection_name, 2, typesense_client)
    assert collection["clean_title"].iloc[0] == title


def test_query_subset_fuzzy_find(typesense_client, test_collection, test_documents):
    title = "godt glort in the heavent"
    expected_title = "gods glory in the heavens"
    collection_name = test_collection["name"]
    collection = make_query_subset(title, collection_name, 2, typesense_client)
    assert collection["clean_title"].iloc[0] == expected_title


def test_query_subset_multiple_found(typesense_client, test_collection, test_documents):
    title = "map of"
    collection_name = test_collection["name"]
    collection = make_query_subset(title, collection_name, 2, typesense_client)
    assert collection.shape[0] > 1


def test_query_subset_drop_token_left(typesense_client, test_collection, test_documents):
    title = "our gods glory in the heavens"
    collection_name = test_collection["name"]
    collection = make_query_subset(title, collection_name, 2, typesense_client)
    assert collection.shape[0] > 0 and collection["num_tokens_dropped"].iloc[0] == 1


def test_query_subset_drop_tokens_right(typesense_client, test_collection, test_documents):
    # Q: is this expected behaviour when setting 'drop_tokens_mode' to 'left_to_right'
    # Does it just mean it *tries* left first then right then left again,
    # Rather than only dropping from left? Seems like it
    title = "gods glory in the heavens above"
    collection_name = test_collection["name"]
    collection = make_query_subset(title, collection_name, 2, typesense_client)
    assert collection.shape[0] == 1


def test_query_subset_drop_tokens_filtered(typesense_client, test_collection, test_documents):
    title = "but our gods glory in the heavens"
    collection_name = test_collection["name"]
    collection = make_query_subset(title, collection_name, 2, typesense_client)
    assert collection.shape[0] == 0


def test_query_subset_not_found(typesense_client, test_collection, test_documents):
    title = "foo bar baz"
    collection_name = test_collection["name"]
    collection = make_query_subset(title, collection_name, 2, typesense_client)
    assert collection.shape[0] == 0
