import re
from enum import Enum
from typing import List, Optional, Annotated, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
from langchain_core.messages import AnyMessage

from ark_v2.data_models.query_models import (
    QueryResult,
    QueryResultEntitiesExist,
    QueryResultGetRelations,
    QueryResultGetEdges,
    QueryResultRelationsExist,
    QueryResultGetTriples,
)
from ark_v2.data_models.graph_models import (
    Triple,
    EdgeVerified,
    TripleVerified,
)


class QuestionTypes(Enum):
    """Enum for existing question types"""

    YES_NO = "yes_no"
    OPEN_ENDED = "open_ended"
    MULTIPLE_CHOICE = "multiple_choice"
    ENTITY_LIST = "entity_list"
    OTHER = "other"


class AgentState(Enum):
    """Enum for different AgentState of the agent"""

    STARTING = "starting"
    SELECT_ANCHOR = "select_anchor"
    SELECT_RELATION = "select_relation"
    RETRIEVE_TRIPLES = "retrieve_triples"
    TOOLS = "tools"  # The state in which the agent has just called a tool
    FINAL = "final"
    NEW_REASONING_STEP = (
        "reasoning"  # This state signals that a new reasoing step should be initiated
    )


class VerifiedModel(BaseModel):
    """A base model for verified models that includes verified results"""

    verificationResults: Optional[QueryResult] = None
    valid: bool = False
    attempt: int = 0


class Keys(BaseModel):
    """A model that holds a list of keys"""

    keys: List[str] = Field(
        description="A list of keys that map to specific entities in a graph, e.g. triples. Keys always have exactly 4 characters.",
    )

    @field_validator("keys")
    def validate_key_length(cls, value):
        """Validate that each key has exactly 4 characters."""
        for item in value:
            if len(item) != 4:
                raise ValueError("Each key must have exactly 4 characters.")
        return value


# Anchor Models


class Anchor(BaseModel):
    """A node of the knowledge graph that has been selected to act as an anchor for exploration"""

    value: str = Field(
        description="The anchor node that should be used to explore the knowledge graph.",
        default="",
    )
    justification: str = Field(
        description="The reasoning behind selecting this anchor node.",
        default="",
    )


class AnchorVerified(VerifiedModel):
    """A verified anchor entity candidate that includes the verification results"""

    verificationResults: Optional[QueryResultEntitiesExist] = None
    anchor: Optional[Anchor] = Field(
        description="The anchor that was verified",
        default=None,
    )


# Relation Models


class Relation(BaseModel):

    value: str = Field(
        description="The relation that should be used to explore the knowledge graph.",
    )
    direction: Literal["outgoing", "incoming"] = Field(
        description=(
            "The direction of the selected relation relative to the anchor. "
            "'outgoing': anchor -> another entity. "
            "'incoming': another entity -> anchor."
        ),
    )
    justification: str = Field(
        description="The reasoning behind selecting this relation and direction.",
        default="",
    )


class RelationVerified(VerifiedModel):
    """A model that holds the verified results of selected relations for a specific anchor entity"""

    candidate: Optional[Relation] = Field(
        description="A relation candidate selected by the LLM.",
        default=None,
    )
    edge: Optional[EdgeVerified] = Field(
        description="A verified edge of the knowledge graph that matches the relations.",
        default=None,
    )


# Triples models


# Exploration record types

StepAction = Literal["continue_path", "switch_candidate", "backtrack", "stop"]
EvidenceType = Literal["kg_triple", "kg_absence", "background", "guess"]
ConclusionStatus = Literal["satisfied", "not_satisfied", "undetermined"]
CandidateStatus = Literal["pending", "excluded", "confirmed"]


class Conclusion(BaseModel):
    """A conclusion proposed by the LLM about one candidate and one condition."""

    candidate: str = Field(
        description=(
            "The entity the conclusion is about, which can be the anchor or an entity "
            "at the other end of the triples. It need not be an answer, e.g. the painter "
            "of a painting. Write it exactly as it appears in the retrieved triples "
            "or the exploration summary, including its ID in parentheses if present."
        ),
    )
    condition: str = Field(
        description=(
            "The condition from the user request that is checked, in short natural language, "
            "e.g. 'shares a border with Esponellà'."
        ),
    )
    status: ConclusionStatus = Field(
        description="Whether the candidate satisfies the condition.",
    )
    evidence_type: EvidenceType = Field(
        description=(
            "'kg_triple': supported by triples retrieved in this step; list their keys. "
            "'kg_absence': the triples retrieved in this step are the complete result for the current anchor and relation, "
            "and the expected entity is not among them; set absent_entity. "
            "'background': based on general knowledge, not on the knowledge graph. "
            "'guess': an unverified assumption, e.g. inferred from a name."
        ),
    )
    keys: List[str] = Field(
        description=(
            "Keys of the triples from this step that support the conclusion. "
            "Required for 'kg_triple', otherwise empty."
        ),
        default=[],
    )
    absent_entity: Optional[str] = Field(
        description=(
            "Only for 'kg_absence': the entity that was expected but is missing from the retrieved triples."
        ),
        default=None,
    )


class ReasoningStepResult(Keys):
    """The LLM output of one reasoning step."""

    implications: str = Field(
        description=(
            "A short summary of implications that were drawn from the retrieved "
            "triples as well as future steps that should be taken to answer the "
            "user request."
        )
    )
    conclusions: List[Conclusion] = Field(
        description=(
            "Conclusions drawn in this step about candidates and conditions of the user request. "
            "Include negative conclusions, e.g. a candidate that does not satisfy a condition."
        ),
        default=[],
    )
    action: StepAction = Field(
        description=(
            "What to do next. "
            "'continue_path': follow the current path further, e.g. explore an entity found in this step. "
            "'switch_candidate': the current candidate is excluded or cannot be verified; continue with another pending candidate. "
            "'backtrack': the current path is not useful; return to an entity from an earlier step and try another relation. "
            "'stop': end exploration because the user request can be fully answered from verified facts, or no further exploration is possible."
        )
    )
    next_anchor: Optional[str] = Field(
        description=(
            "The entity you intend to explore in the next reasoning step, written exactly as it appears "
            "in the retrieved triples or the exploration summary, including its ID in parentheses "
            "if present. Leave empty if the action is 'stop'."
        ),
        default=None,
    )
    discard_step: bool = Field(
        description=(
            "Set to True only if the triples retrieved in this step are irrelevant to the user request. "
            "A discarded step is kept in the record but not used as evidence. "
            "Discarding a step does not stop exploration."
        ),
        default=False,
    )


class ReasoningStepResultVerified(VerifiedModel):
    """A model that holds the verified results of selected triples for a specific anchor entity and relations"""

    result: Optional[ReasoningStepResult] = Field(
        description="The inferred result of the reasoning step that includes the selected triples and implications.",
        default=None,
    )
    triples: List[TripleVerified] = Field(
        description="A list of verified triples that match the selected triples.",
        default=[],
    )
    invalid_keys: Optional[List[str]] = Field(
        description="A list of keys that were selected but are invalid.",
        default=[],
    )

    def get_triples_list(self) -> List[str]:
        """Get a string representation of the selected triples"""
        return [str(triple) for triple in self.triples]


class ReasoningStep(BaseModel):
    """A single reasoning step comprises the following components:
    1. A single anchor entity that is selected to explore the knowledge graph
    2. Relations that were retrieved from the knowledge graph based on the anchor entity
    3. A single relation that was selected from the retrieved relations to be used for exploration
    4. Triples that were retrieved from the knowledge graph based on the anchor entity and selected relation
    5. A reasoning result that includes the selected triples and implications
    """

    anchor: Optional[AnchorVerified] = None
    relations_retrieved: Optional[List[EdgeVerified]] = []
    relation_selected: Optional[RelationVerified] = None
    triples_retrieved: Optional[List[TripleVerified]] = None
    result: Optional[ReasoningStepResultVerified] = None
    finished: bool = False
    discarded: bool = False

    def get_triples_retrieved_str(self) -> str:
        """Get a string representation of the retrieved triples"""
        if self.triples_retrieved is None:
            return "No triples retrieved."
        return "\n".join([str(triple) for triple in self.triples_retrieved])

    def get_triples_retrieved(self) -> List[Dict[str, Any]]:
        """Get a list of dictionaries representing the retrieved triples"""
        if self.triples_retrieved is None:
            return []
        return [triple.get_dict() for triple in self.triples_retrieved]

    def get_keys_triples_retrieved(self) -> List[str]:
        """Get a list of keys for the retrieved triples"""
        if self.triples_retrieved is None:
            return []
        return [triple.key for triple in self.triples_retrieved]

    def get_relations_retrieved(self) -> List[str]:
        """Get a string representation of the retrieved relations"""
        if self.relations_retrieved is None:
            return []
        return [relation.get_relation() for relation in self.relations_retrieved]

    def get_keys_relations_retrieved(self) -> List[str]:
        """Get a list of keys for the retrieved relations"""
        if self.relations_retrieved is None:
            return []
        return [relation.key for relation in self.relations_retrieved]

    def get_dict_triples_retrieved(self) -> Dict[str, Triple]:
        """Get a dictionary representation of the retrieved triples"""
        if self.triples_retrieved is None:
            return {}
        return {triple.key: triple for triple in self.triples_retrieved}


# Answers


class FinalAnswer(BaseModel):
    """Final result of the reasoning process"""

    arisedQuestion: str = Field(
        description="A question that came up during the reasoning process that should be answered to improve your answer.",
        default="",
    )
    ambigoutyOfRequest: bool = Field(
        description="Flag indicating if the initial request is ambiguous and cant be answered directly",
    )
    justification: str = Field(
        description="The reasoning behind the final answer",
    )


class FinalAnswerYesNo(FinalAnswer):
    """Final answer for yes/no questions"""

    answer: Optional[bool] = Field(
        description="The final answer to the user request, either True or False. If the question couldn't be answered, it should be None.",
    )


class FinalAnswerEntityList(FinalAnswer):
    """Final answer for entity list questions"""

    answer: Optional[List[str]] = Field(
        description=(
            "A list of knowledge graph entities that answer the user request. "
            "Use None when the answer cannot be determined from the retrieved "
            "knowledge graph information. Use an empty list only when the "
            "question is answerable but has no matching entities."
        )
    )


class FinalAnswerEntityListVerified(VerifiedModel):
    """Final answer for entity list questions with verification results"""

    answer: FinalAnswerEntityList


# Exploration Record


def normalize_entity_name(name: str) -> str:
    """Normalize an entity name for matching (whitespace and case)."""
    return " ".join(name.split()).casefold()

def strip_entity_id(name: str) -> str:
    """Remove a trailing Wikidata ID such as ' (Q123)' from an entity name."""
    return re.sub(r"\s*\(Q[1-9]\d*\)\s*$", "", name.strip())

def get_entity_id(name: str) -> Optional[str]:
    """Return the trailing Wikidata ID of an entity name, e.g. 'Q123', or None."""
    match = re.search(r"\((Q[1-9]\d*)\)\s*$", name.strip())
    return match.group(1) if match else None


def same_entity(a: str, b: str) -> bool:
    """
    Check whether two entity names refer to the same entity.
    Names must match without ID, and IDs must not conflict, e.g.
    "John Smith (Q10)" matches "John Smith", but not "John Smith (Q20)".
    """
    if normalize_entity_name(strip_entity_id(a)) != normalize_entity_name(
        strip_entity_id(b)
    ):
        return False
    id_a, id_b = get_entity_id(a), get_entity_id(b)
    # True if both IDs are equal or at least one name has no ID
    return id_a is None or id_b is None or id_a == id_b


class ConclusionRecord(BaseModel):
    """A conclusion after program-side verification."""

    conclusion_id: int
    iteration: int = Field(description="Reasoning iteration of the conclusion.")
    candidate: str
    condition: str
    constraint_id: Optional[str] = Field(
        default=None,
        description="Reference to the constraint list.",
    )
    status: ConclusionStatus
    evidence_type: EvidenceType
    triples: List[TripleVerified] = []
    absent_entity: Optional[str] = None
    query: Optional[Dict[str, str]] = Field(
        default=None,
        description="Anchor, relation and direction of the step.",
    )
    verified: bool = Field(
        default=False,
        description="True only for kg_triple or kg_absence conclusions that passed verification.",
    )
    rejection_reason: Optional[str] = None


class CandidateRecord(BaseModel):
    """An entity retrieved during exploration, independent of whether it was cited."""

    name: str
    source_iteration: int
    status: CandidateStatus = "pending"
    conclusion_ids: List[int] = []


class ExplorationRecord(BaseModel):
    """Exploration state that is never removed when a reasoning step is reset."""

    constraints: List[Dict[str, Any]] = Field(
        default=[],
        description="Constraint list; filled from stage B on.",
    )
    candidates: List[CandidateRecord] = []
    conclusions: List[ConclusionRecord] = []

    def find_candidate(self, name: str) -> Optional[CandidateRecord]:
        """
        Find the existing candidate that a conclusion's candidate name refers to.
        Exact name match first, otherwise a unique match by same_entity.
        Returns None if nothing or more than one candidate matches.
        """
        target = normalize_entity_name(name)
        for candidate in self.candidates:
            if normalize_entity_name(candidate.name) == target:
                return candidate

        matches = [
            candidate
            for candidate in self.candidates
            # True if both entities have the same name and ID, or same name but at least one name has no ID.
            if same_entity(candidate.name, name)
        ]
        return matches[0] if len(matches) == 1 else None


# Runtime State


class RuntimeState(BaseModel):
    """The RuntimeState model that holds the answer to the given question"""

    # session_id: str
    question: str = Field(
        description="The user question that should be answered",
        default="",
    )
    currentState: AgentState = AgentState.STARTING
    messages: Annotated[
        List[AnyMessage], "The message history used in agent prompts"
    ] = []
    messages_full: Annotated[List[AnyMessage], "The full message history"] = []
    reasoningSteps: List[ReasoningStep] = Field(
        description="List of reasoning steps",
        default=[],
    )
    exploration: ExplorationRecord = Field(
        description="Exploration record kept across resets",
        default_factory=ExplorationRecord,
    )
    iteration: int = 0
    continue_exploration: bool = True
    termination_reason: Optional[str] = Field(
        default=None,
        description="The reason exploration ended before final answer generation.",
    )
    finalAnswer: Optional[FinalAnswer] = None

    def append_message(self, message: AnyMessage) -> None:
        """Append a message to the message history"""
        self.messages.append(message)
        self.messages_full.append(message)

    def extend_messages(self, messages: List[AnyMessage]) -> None:
        """Extend the message history with a list of messages"""
        self.messages.extend(messages)
        self.messages_full.extend(messages)
