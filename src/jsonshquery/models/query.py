from typing import List, Dict, Any, Union, Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict

class MatchAll(BaseModel):
    match_all: Dict[str, Any]

class MatchClause(BaseModel):
    match: Dict[str, Any]

class MatchPhraseClause(BaseModel):
    match_phrase: Dict[str, Any]

class MatchPhrasePrefixClause(BaseModel):
    match_phrase_prefix: Dict[str, Any]

class MultiMatchQuery(BaseModel):
    query : str
    fields : List[str]

class MultiMatchClause(BaseModel):
    multi_match: MultiMatchQuery

class TermClause(BaseModel):
    term: Dict[str, Any]

class TermsClause(BaseModel):
    terms: Dict[str, List[Any]]

class RangeClause(BaseModel):
    range: Dict[str, Dict[str, Any]]

class ExistsQuery(BaseModel):
    field : str

class ExistsClause(BaseModel):
    exists: ExistsQuery

class PrefixClause(BaseModel):
    prefix : Dict[str, Any]

class WildcardClause(BaseModel):
    wildcard: Dict[str, Any]

class RegexpClause(BaseModel):
    regexp: Dict[str, Any]

class BoolContainer(BaseModel):
    must: Optional[List["Query"]] = Field(default_factory=list)
    filter: Optional[List["Query"]] = Field(default_factory=list)
    must_not: Optional[List["Query"]] = Field(default_factory=list)
    should: Optional[List["Query"]] = Field(default_factory=list)

class BoolClause(BaseModel):
    bool: BoolContainer

Query = Annotated[Union[
    MatchAll,
    MatchClause,
    MatchPhraseClause,
    MatchPhrasePrefixClause,
    MultiMatchClause,
    TermClause,
    TermsClause,
    ExistsClause,
    RangeClause,
    PrefixClause,
    WildcardClause,
    RegexpClause,
    BoolClause
], Field(discriminator=None)]

BoolContainer.model_rebuild()

class ESRequestBody(BaseModel):
    result_path : Optional[str] = None
    query: Optional[Query] = None
    size: Optional[int] = Field(default=10, ge=0)
    source: Optional[Union[bool, str, List[str], Dict[str, List[str]]]] = Field(
        alias="_source",
        default=None,
        description="Filter returned source fields"
    )
    model_config = ConfigDict(
        populate_by_name=True  # Allows both 'source' and '_source' during parsing
    )