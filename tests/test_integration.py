import pytest
import sys
import os
import json

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from jsonshquery.core import search_by_query


# Load test data
def load_test_data():
    test_data_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'test_data.json')
    with open(test_data_path, 'r') as f:
        return json.load(f)


test_data = load_test_data()


def test_simple_term_query():
    """Test simple term query"""
    query = {
        "query": {
            "term": {"category": "Electronics"}
        }
    }
    results = search_by_query(test_data, query)["hits"]
    assert len(results) == 2  # Should find 2 electronics products
    assert all(doc["category"] == "Electronics" for doc in results)


def test_simple_match_query():
    """Test simple match query"""
    query = {
        "query": {
            "match": {"description": "great"}
        }
    }
    results = search_by_query(test_data, query)["hits"]
    assert len(results) >= 1  # Should find at least one product with "great"
    assert any("great" in doc["description"].lower() for doc in results)


def test_bool_must_query():
    """Test bool query with must clause"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"category": "Electronics"}},
                    {"term": {"in_stock": True}}
                ]
            }
        }
    }
    results = search_by_query(test_data, query)["hits"]
    assert all(doc["category"] == "Electronics" for doc in results)
    assert all(doc["in_stock"] == True for doc in results)


def test_bool_must_not_query():
    """Test bool query with must_not clause"""
    query = {
        "query": {
            "bool": {
                "must_not": [
                    {"term": {"category": "Clothing"}}
                ]
            }
        }
    }
    results = search_by_query(test_data, query)["hits"]
    assert len(results) == 4  # Should exclude the clothing product
    assert all(doc["category"] != "Clothing" for doc in results)


def test_bool_combined_query():
    """Test combined bool query with must and must_not"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"in_stock": True}}
                ],
                "must_not": [
                    {"term": {"category": "Clothing"}}
                ]
            }
        }
    }
    results = search_by_query(test_data, query)["hits"]
    assert all(doc["in_stock"] == True for doc in results)
    assert all(doc["category"] != "Clothing" for doc in results)


def test_match_phrase_query():
    """Test match phrase query"""
    query = {
        "query": {
            "match_phrase": {"description": "small space"}
        }
    }
    results = search_by_query(test_data, query)["hits"]
    assert len(results) >= 1  # Should find at least one product with "small space"
    assert any("small space" in doc["description"].lower() for doc in results)


def test_multi_match_query():
    """Test multi match query across multiple fields"""
    query = {
        "query": {
            "multi_match": {
                "query": "great",
                "fields": ["name", "description"]
            }
        }
    }
    results = search_by_query(test_data, query)["hits"]
    assert len(results) >= 1  # Should find at least one product


def test_prefix_query():
    """Test prefix query"""
    query = {
        "query": {
            "prefix": {"name": "Product"}
        }
    }
    results = search_by_query(test_data, query)["hits"]
    assert all(doc["name"].startswith("Product") for doc in results)


def test_exists_query():
    """Test exists query"""
    query = {
        "query": {
            "exists": {"field": "tags"}
        }
    }
    results = search_by_query(test_data, query)["hits"]
    assert all("tags" in doc for doc in results)


def test_terms_query():
    """Test terms query with multiple values"""
    query = {
        "query": {
            "terms": {"category": ["Electronics", "Furniture"]}
        }
    }
    results = search_by_query(test_data, query)["hits"]
    assert all(doc["category"] in ["Electronics", "Furniture"] for doc in results)


def test_complex_bool_query():
    """Test complex bool query with multiple clauses"""
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"description": "great"}}
                ],
                "must_not": [
                    {"term": {"category": "Furniture"}}
                ],
                "should": [
                    {"term": {"in_stock": True}}
                ]
            }
        }
    }
    results = search_by_query(test_data, query)["hits"]
    assert any("great" in doc["description"].lower() for doc in results)
    assert all(doc["category"] != "Furniture" for doc in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
