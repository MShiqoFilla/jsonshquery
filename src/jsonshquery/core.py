from typing import List, Dict
from hashlib import md5
import fnmatch
import json
import re

def get_nested_value(data, field_path):
    """
    Safely access nested fields using dot notation (e.g., "address.city")
    Returns None if any part of the path doesn't exist
    """
    keys = field_path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current

def field_exists(data, field_path):
    """
    Check if a nested field exists
    """
    keys = field_path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return False
    return True

def generate_id(text:str):
    """Generate md5 hash as id of documents"""
    return md5(text.encode()).hexdigest()

def check_term(field, keyword, data):
    """Apply term query to single document"""
    value = get_nested_value(data, field)
    if value is None:
        return False
    if isinstance(value, list):
        if keyword in value:
            return True
    if value == keyword:
        return True

def check_terms(field, keywords, data):
    """Apply terms query to single document"""
    value = get_nested_value(data, field)
    if value is not None and value in keywords:
        return True

def check_prefix(field, prefix, data):
    """Apply prefix query to single document"""
    try:
        value = get_nested_value(data, field)
        if value is not None and str(value).startswith(prefix):
            return True
    except (AttributeError, TypeError):
        return False

def check_match_all():
    """
    Match all documents (when no specific query is given)
    This is used for match_all queries like {"match_all": {}}
    """
    return True

def check_match(field, text, data):
    """Apply match query to single document"""
    value = get_nested_value(data, field)
    if value is None:
        return False
    if isinstance(value, str):
        tokens_to_match = [t.lower() for t in text.split(" ")]
        if any(token in str(value).lower() for token in tokens_to_match):
            return True
    elif isinstance(value, (str, float)):
        if value == text:
            return True

def check_match_phrase(field, text, data):
    """Apply match_phrase query to single document"""
    value = get_nested_value(data, field)
    if value is None:
        return False
    target = re.sub(r'\s+', ' ', str(value)).strip()
    text = re.sub(r'\s+', ' ', text).strip()
    
    if text.lower() in target.lower():
        return True

def check_match_phrase_prefix(field, text, data):
    """Apply match_phrase_prefix query to single document"""
    if check_match_phrase(field, text, data) and check_prefix(field, text, data):
        return True

def check_multi_match(fields, text, data):
    """Apply multi_match query to single document"""
    for field in fields:
        if check_match(field, text, data):
            return True

def check_exists(field, data):
    """Apply exists query to single document"""
    return field_exists(data, field)

def check_wildcard(field, pattern, data):
    """Apply wildcard query to single document"""
    value = get_nested_value(data, field)
    if value is None:
        return False
    if fnmatch.fnmatch(value, pattern):
        return True
    
def check_regexp(field, pattern, data):
    """Apply regexp query to single document"""
    value = get_nested_value(data, field)
    if value is None:
        return False
    if re.fullmatch(rf"{pattern}", value):
        return True

def check_range(field, range_payload:dict, data):
    """Apply range query to single document, p.s: only works to numerical value, int or float"""
    value = get_nested_value(data, field)
    ranges_type = list(range_payload.keys())
    lower_type = None
    upper_type = None
    if "gte" in ranges_type:
        lower_type = "gte"
    elif "gt" in ranges_type:
        lower_type = "gt"

    if "lte" in ranges_type:
        upper_type = "lte"
    elif "lt" in ranges_type:
        upper_type = "lt"

    lower_limit = range_payload.get("gte") or range_payload.get("gt")
    upper_limit = range_payload.get("lte") or range_payload.get("lt")

    if lower_limit is not None and upper_limit is not None:
        if lower_type == "gt" and upper_type == "lt":
            if lower_limit < value and value < upper_limit:
                return True
        elif lower_type == "gt" and upper_type == "lte":
            if lower_limit < value and value <= upper_limit:
                return True
        elif lower_type == "gte" and upper_type == "lt":
            if lower_limit <= value and value < upper_limit:
                return True
        elif lower_type == "gte" and upper_type == "lte":
            if lower_limit <= value and value <= upper_limit:
                return True

    if lower_limit is not None and upper_limit is None:
        if lower_type == "gt":
            if lower_limit < value:
                return True
        elif lower_type == "gte":
            if lower_limit <= value:
                return True
    elif lower_limit is None and upper_limit is not None:
        if upper_type == "lt":
            if value < upper_limit:
                return True
        elif upper_type == "lte":
            if value <= upper_limit:
                return True
               
def query_by_term(query, hashed_dicts):
    """
    Query a single term clause to list of dictionaries
    Return:
        List[str] : list of ids that matched query 
    """
    results = set()
    field, keyword = next(iter(query["term"].items()))
    for hash_id, doc in hashed_dicts.items():
        if check_term(field, keyword, doc):
            results.add(hash_id)
    return results

def query_by_terms(query, hashed_dicts):
    """
    Query a single terms clause to list of dictionaries
    Return:
        List[str] : list of ids that matched query 
    """
    results = set()
    field, keywords = next(iter(query["terms"].items()))
    for hash_id, doc in hashed_dicts.items():
        if check_terms(field, keywords, doc):
            results.add(hash_id)
    return results

def query_by_match_all(query, hashed_dicts):
    """
    Query a single match_all clause to list of dictionaries
    Return:
        List[str] : list of ids that matched query 
    """
    results = set()
    for hash_id, doc in hashed_dicts.items():
        if check_match_all():
            results.add(hash_id)
    return results

def query_by_match(query, hashed_dicts):
    """
    Query a single match clause to list of dictionaries
    Return:
        List[str] : list of ids that matched query 
    """
    results = set()
    field, text = next(iter(query["match"].items()))
    for hash_id, doc in hashed_dicts.items():
        if check_match(field, text, doc):
            results.add(hash_id)
    return results

def query_by_match_phrase(query, hashed_dicts):
    """
    Query a single match_phrase clause to list of dictionaries
    Return:
        List[str] : list of ids that matched query 
    """
    results = set()
    field, text = next(iter(query["match_phrase"].items()))
    for hash_id, doc in hashed_dicts.items():
        if check_match_phrase(field, text, doc):
            results.add(hash_id)
    return results

def query_by_match_phrase_prefix(query, hashed_dicts):
    """
    Query a single match_phrase_prefix clause to list of dictionaries
    Return:
        List[str] : list of ids that matched query 
    """
    results = set()
    field, text = next(iter(query["match_phrase_prefix"].items()))
    for hash_id, doc in hashed_dicts.items():
        if check_match_phrase_prefix(field, text, doc):
            results.add(hash_id)
    return results

def query_by_multi_match(query, hashed_dicts):
    """
    Query a single multi_match clause to list of dictionaries
    Return:
        List[str] : list of ids that matched query 
    """
    results = set()
    fields = query["multi_match"]["fields"]
    text = query["multi_match"]["query"]
    for hash_id, doc in hashed_dicts.items():
        if check_multi_match(fields, text, doc):
            results.add(hash_id)
    return results

def query_by_prefix(query, hashed_dicts):
    """
    Query a single prefix clause to list of dictionaries
    Return:
        List[str] : list of ids that matched query 
    """
    results = set()
    field, prefix = next(iter(query["prefix"].items()))
    for hash_id, doc in hashed_dicts.items():
        if check_prefix(field, prefix, doc):
            results.add(hash_id)
    return results

def query_by_exists(query, hashed_dicts):
    """
    Query a single exists clause to list of dictionaries
    Return:
        List[str] : list of ids that matched query 
    """
    results = set()
    field_to_look_up = query["exists"]["field"]
    for hash_id, doc in hashed_dicts.items():
        if check_exists(field_to_look_up, doc):
            results.add(hash_id)
    return results

def query_by_wildcard(query, hashed_dicts):
    """
    Query a single wildcard clause to list of dictionaries
    Return:
        List[str] : list of ids that matched query 
    """
    results = set()
    field = next(iter(query["wildcard"].keys()))
    pattern = query["wildcard"][field]["value"]
    for hash_id, doc in hashed_dicts.items():
        if check_wildcard(field, pattern, doc):
            results.add(hash_id)
    return results

def query_by_regexp(query, hashed_dicts):
    """
    Query a single regexp clause to list of dictionaries
    Return:
        List[str] : list of ids that matched query 
    """
    results = set()
    field = next(iter(query["regexp"].keys()))
    pattern = query["regexp"][field]["value"]
    for hash_id, doc in hashed_dicts.items():
        if check_regexp(field, pattern, doc):
            results.add(hash_id)
    return results

def query_by_range(query, hashed_dicts):
    """
    Query a single range clause to list of dictionaries
    Return:
        List[str] : list of ids that matched query 
    """
    results = set()
    field, range_payload = next(iter(query["range"].items()))
    for hash_id, doc in hashed_dicts.items():
        if check_range(field, range_payload, doc):
            results.add(hash_id)
    return results

functions = {
    "term" : query_by_term,
    "terms" : query_by_terms,
    "match_all" : query_by_match_all,
    "match" : query_by_match,
    "match_phrase" : query_by_match_phrase,
    "match_phrase_prefix" : query_by_match_phrase_prefix,
    "multi_match" : query_by_multi_match,
    "prefix" : query_by_prefix,
    "exists" : query_by_exists,
    "wildcard" : query_by_wildcard,
    "regexp" : query_by_regexp,
    "range" : query_by_range
}

def query_by_must(queries, hashed_dicts):
    """Query by Boolean clause: must"""
    ids_results = []
    for query in queries:
        query_type = list(query.keys())[0]
        ids_results.append(functions[query_type](query, hashed_dicts))

    return set.intersection(*ids_results)

def query_by_filter(queries, hashed_dicts):
    """Query by Boolean clause: filter"""
    ids_results = []
    for query in queries:
        query_type = list(query.keys())[0]
        ids_results.append(functions[query_type](query, hashed_dicts))

    return set.intersection(*ids_results)

def query_by_must_not(queries, hashed_dicts):
    """Query by Boolean clause: must_not"""
    ids_results = []
    for query in queries:
        query_type = list(query.keys())[0]
        ids_results.append(functions[query_type](query, hashed_dicts))

    all_ids = set(hashed_dicts.keys())
    union_ids = set.union(*ids_results)
    return all_ids.difference(union_ids)

def query_by_should(queries, hashed_dicts):
    """Query by Boolean clause: should"""
    ids_results = []
    for query in queries:
        query_type = list(query.keys())[0]
        ids_results.append(functions[query_type](query, hashed_dicts))

    return set.union(*ids_results)

bool_functions = {
    "must" : query_by_must,
    "must_not" : query_by_must_not,
    "should" : query_by_should,
    "filter" : query_by_filter
}

def get_only_some_fields(data:dict, source:List[str]=None):
    """
    Return the result for only certain fields
    """
    if not source:
        return data
    source_only = {}
    for field in source:
        source_only[field] = data.get(field)
    return source_only

def search_by_query(data:List[Dict], payload:Dict):
    """
    Function to apply Elasticsearch Query DSL to array of object/dictionaries
    Args:
        data: List[Dict] ==> list of data
        payload: Dict ==> query
    """
    source = payload.get("source")
    size = payload.get("size")
    query = payload.get("query")

    if not query:
        query = {
            "match_all" : {}
        }

    try:
        hashes = {generate_id(json.dumps(d)) : d for d in data}
        is_single_query = True

        if query.get("bool"):
            is_single_query = False

        if is_single_query:
            query_type = list(query.keys())[0]
            queried_ids = functions[query_type](query, hashes)

        if not is_single_query:
            ids_result = {}
            bool_queries = query["bool"]
            number_of_query_types = len(bool_queries)
            for query_type, list_query in bool_queries.items():
                if number_of_query_types > 1 and query_type == "should":
                    continue
                ids_result[query_type] = bool_functions[query_type](list_query, hashes)

            list_of_ids_set = list(ids_result.values())
            queried_ids = set.intersection(*list_of_ids_set)
        
        if size:
            result = [get_only_some_fields(hashes[id], source) for id in queried_ids][:size]
        else:
            result = [get_only_some_fields(hashes[id], source) for id in queried_ids]
        return {
            "count" : len(result),
            "hits" : result
        }
    except Exception as e:
        raise ValueError("Please check again your query body!")