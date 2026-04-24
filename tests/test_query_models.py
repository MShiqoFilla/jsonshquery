import pytest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from jsonshquery.models.query import (
    ESRequestBody, MatchClause, TermClause, BoolClause,
    MatchPhraseClause, MultiMatchClause, PrefixClause, ExistsClause
)


def test_match_clause_parsing():
    """Test parsing match query"""
    match_query = {"match": {"description": "great device"}}
    clause = MatchClause(**match_query)
    assert clause.match == {"description": "great device"}


def test_term_clause_parsing():
    """Test parsing term query"""
    term_query = {"term": {"category": "Electronics"}}
    clause = TermClause(**term_query)
    assert clause.term == {"category": "Electronics"}


def test_bool_clause_parsing():
    """Test parsing bool query"""
    bool_query = {
        "bool": {
            "must": [
                {"term": {"category": "Electronics"}}
            ],
            "must_not": [
                {"term": {"category": "Clothing"}}
            ]
        }
    }
    clause = BoolClause(**bool_query)
    assert len(clause.bool.must) == 1
    assert len(clause.bool.must_not) == 1


def test_es_request_body_parsing():
    """Test parsing complete Elasticsearch request body"""
    es_query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"category": "Electronics"}}
                ]
            }
        },
        "size": 10
    }
    request = ESRequestBody(**es_query)
    assert request.size == 10
    assert request.query is not None


def test_match_phrase_clause():
    """Test match phrase query"""
    phrase_query = {"match_phrase": {"description": "great device"}}
    clause = MatchPhraseClause(**phrase_query)
    assert clause.match_phrase == {"description": "great device"}


def test_multi_match_clause():
    """Test multi match query"""
    multi_query = {"multi_match": {"query": "device", "fields": ["name", "description"]}}
    clause = MultiMatchClause(**multi_query)
    assert clause.multi_match.query == "device"
    assert clause.multi_match.fields == ["name", "description"]


def test_prefix_clause():
    """Test prefix query"""
    prefix_query = {"prefix": {"name": "Product"}}
    clause = PrefixClause(**prefix_query)
    assert clause.prefix == {"name": "Product"}


def test_exists_clause():
    """Test exists query"""
    exists_query = {"exists": {"field": "category"}}
    clause = ExistsClause(**exists_query)
    assert clause.exists.field == "category"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
