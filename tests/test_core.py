import pytest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from jsonshquery.core import (
    check_term, check_terms, check_match, check_match_phrase,
    check_prefix, check_multi_match, check_exists,
    query_by_term, query_by_match
)

# Test data
test_documents = [
    {"id": 1, "name": "Product A", "category": "Electronics", "price": 99.99, "in_stock": True},
    {"id": 2, "name": "Product B", "category": "Furniture", "price": 199.99, "in_stock": False},
    {"id": 3, "name": "Product C", "category": "Electronics", "price": 299.99, "in_stock": True},
]


def test_check_term():
    """Test term matching"""
    assert check_term("category", "Electronics", test_documents[0]) == True
    assert not check_term("category", "Furniture", test_documents[0])  # None or False


def test_check_terms():
    """Test terms matching"""
    assert check_terms("category", ["Electronics", "Furniture"], test_documents[0]) == True
    assert not check_terms("category", ["Furniture"], test_documents[0])  # None or False


def test_check_match():
    """Test match text search"""
    assert check_match("name", "Product", test_documents[0]) == True
    assert not check_match("name", "Furniture", test_documents[0])  # None or False
    assert check_match("name", "product a", test_documents[0]) == True  # Case insensitive


def test_check_prefix():
    """Test prefix matching"""
    assert check_prefix("name", "Product", test_documents[0]) == True
    assert check_prefix("name", "Prod", test_documents[0]) == True
    assert not check_prefix("name", "Furn", test_documents[0])  # None or False


def test_check_exists():
    """Test field existence"""
    assert check_exists("category", test_documents[0]) == True
    assert check_exists("name", test_documents[0]) == True
    assert check_exists("nonexistent", test_documents[0]) == False


def test_query_by_term():
    """Test term query"""
    query = {"term": {"category": "Electronics"}}
    hashed_dicts = {f"doc_{doc['id']}": doc for doc in test_documents}
    results = query_by_term(query, hashed_dicts)
    assert len(results) == 2  # Two electronics products


def test_query_by_match():
    """Test match query"""
    query = {"match": {"name": "Product"}}
    hashed_dicts = {f"doc_{doc['id']}": doc for doc in test_documents}
    results = query_by_match(query, hashed_dicts)
    assert len(results) == 3  # All products have "Product" in name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
