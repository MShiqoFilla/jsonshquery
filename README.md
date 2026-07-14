# JSONSHQUERY

[![PyPI version](https://img.shields.io/pypi/v/jsonshquery)](https://pypi.org/project/jsonshquery/)
[![Python Versions](https://img.shields.io/pypi/pyversions/jsonshquery)](https://pypi.org/project/jsonshquery/)
[![License](https://img.shields.io/pypi/l/jsonshquery)](LICENSE)
[![Downloads](https://static.pepy.tech/badge/jsonshquery)](https://pepy.tech/projects/jsonshquery)

Query JSON files using Elasticsearch Query DSL syntax.

## Overview
Jsonshquery lets you query array of object in a json file or python dictionary by following Elasticsearch query DSL. If you are familiar with Elasticsearch, then there shouldn't be any problem for you to use this tool. 

PyPI : https://pypi.org/project/jsonshquery

## Features

- Query JSON files (arrays of objects) using Elasticsearch Query DSL
- Support for basic query clauses: `term`, `terms`, `match`, `match_phrase`, `multi_match`, `prefix`, `exists`
- Boolean queries: `must`, `must_not`, `should`, `filter`
- Nested field support using dot notation (e.g., `address.city`)
- Interactive CLI with JSON syntax highlighting and auto-completion

## Installation

```bash
pip install jsonshquery
```

## Usage

### Interactive CLI

To start interacting with the command line, run this command.
```bash
jsonshquery --file <./path/to/file.json>
```
Look at this example. Given a JSON file `data.json`:
```json
[
  {
        "id": 2,
        "name": "Product B",
        "category": "Furniture",
        "price": 89.50,
        "in_stock": true,
        "tags": ["wood"],
        "supplier": {"name": "Supplier Y", "country": "Indonesia"},
        "description": "A durable wooden furniture piece crafted with quality materials, suitable for home interiors, providing comfort, stability, and aesthetic appeal for daily use."
    },
    {
        "id": 3,
        "name": "Product C",
        "category": "Clothing",
        "price": 29.99,
        "in_stock": true,
        "tags": ["fashion"],
        "supplier": {"name": "Supplier Z", "country": "Vietnam"},
        "description": "A stylish clothing item made with breathable fabric, designed for comfort and versatility, suitable for casual wear and adaptable to various weather conditions."
    },
    {
        "id": 5,
        "name": "Product E",
        "category": "Furniture",
        "price": 59.99,
        "in_stock": true,
        "tags": ["sale"],
        "supplier": {"name": "Supplier A", "country": "Indonesia"},
        "description": "A compact furniture unit designed for comfort, offering functional storage, lightweight structure, and modern appearance suitable for apartments and offices."
    }
]
```

Start the interactive CLI:
```bash
jsonshquery --file data.json
```

This Elasticsearch-style query demonstrates the capabilities of `jsonshquery`:

```json
{
  "result_path" : "./result/query_test.json",
  "_source" : ["id", "name", "category", "description"],
  "query": {
    "bool": {
      "must": [
        { "match" : { "description": "comfort" }},
        { "range" : { "price" : { "gte" : 40, "lte" : 100 }}},
        { "term" : { "in_stock" : true }},
        { "term" : { "supplier.country" : "Indonesia" }}
      ],
      "must_not": [
        { "term": { "category": "Clothing" }}
      ]
    }
  }
};
```

**End your query with `;` and press Enter to execute**. When you use this interactive CLI the result of the query will be created in a json file. 

The `result_path` field is optional, you use it to specify in which directory the query result will be created, if you don't specify it by default the file name will be `jsonshquery_result.json`. This is the expected output format:

```json
{
    "count": 2,
    "hits": [
        {
            "id": 2,
            "name": "Product B",
            "category": "Furniture",
            "description": "A durable wooden furniture piece crafted with quality materials, suitable for home interiors, providing comfort, stability, and aesthetic appeal for daily use."
        },
        {
            "id": 5,
            "name": "Product E",
            "category": "Furniture",
            "description": "A compact furniture unit designed for comfort, offering functional storage, lightweight structure, and modern appearance suitable for apartments and offices."
        }
    ]
}
```

### Python Module

You can also use `jsonshquery` as module
```python
from jsonshquery import Jsonshquery

data = [
    {"id": 1, "name": "Product A", "category": "Furniture", "price": 99.99},
    {"id": 2, "name": "Product B", "category": "Electronics", "price": 49.99}
]

query = {
    "query": {
        "bool": {
            "must": [
                {"term": {"category": "Furniture"}}
            ]
        }
    }
}

jq = Jsonshquery(data)
result = jq.search_by_query(query)
print(f"Found {result['count']} products")
```

## Supported Query Types

### Leaf Query Clauses

- **term**: Exact field match
- **terms**: Field matches one of multiple values
- **match**: Full-text search
- **match_phrase**: Phrase matching
- **multi_match**: Search across multiple fields
- **match_all**: just return all documents
- **prefix**: Prefix matching
- **match_phrase_prefix** : Combination of `match_phrase` and `prefix`
- **range** : Field value within range
- **exists**: Check if field exists
- **wildcard** : Match by pattern (*, ?, etc)
- **regexp** : Match by regex

### Boolean Queries

- **must**: All clauses must match (AND)
- **must_not**: All clauses must not match (NOT)
- **should**: At least one clause must match (OR)
- **filter**: Same as must, but no scoring

### Other Keywords

- **_source**: Fields that wanted to be returned, if not specified it will return complete documents.
- **size**: Limit the number of matching documents to return, if not specified it will return all matching documents.

## Some Important Notes

Native elasticsearch implements scoring on query result, on the other hand, jsonshquery doesn't do that. Every matched documents are purely based on the query given without any scoring process, so it is more like filtering. Therefore keyword `filter` and `must` actually works the same here.

In Elasticsearch, if `should` keyword is being used together with `must` it will become a scoring booster to the documents that matched with `must` clause, but since `jsonshquery` doesn't care about scoring, using `should` with `must` is kinda useless and the codebase itself ignore that. Anyway if `should` is the only boolean clause used in `bool`, `jsonshquery` and elasticsearch will work pretty equal, that is, it becomes an OR statement for the leaf clauses inside `should`.

`range` clause currently limited to only value with numerical type, you cannot do date or time filtering using `range` here. `nested` keyword is also not available.

`jsonshquery` is not yet optimized for speed, our current objective is to make it works as expected. But you generally won't notice long query execution time for even medium to high size documents.

This tool will load your json data into memory, so you might have some consideration when your json file has a huge size.


## Possible Errors

- Data is not in form list of objects/dictionaries
- Invalid JSON body
- Malformed query body

## License

MIT License - see LICENSE file for details.
