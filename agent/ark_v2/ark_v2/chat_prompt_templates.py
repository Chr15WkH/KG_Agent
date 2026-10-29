import json
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate


## Prompts
def get_prompt_system_description() -> ChatPromptTemplate:
    return ChatPromptTemplate(
        [
            (
                "system",
                "You are an AI agent that answers user questions by exploring a knowledge graph (KG) step-by-step. "
                "You are guided through the process of selecting and retrieving information to answer the request. "
                "Each step will be provided as a separate detailed system message. "
                "\n\nProcess:\n"
                "1. Receive the user request and (optionally) a summary of previous reasoning steps.\n"
                "2. Create a new reasoning step:\n"
                "   2.1 Select ONE specific anchor entity from the KG to explore next.\n"
                "   2.2 From the anchor entity's available relation-direction pairs, select exactly ONE pair to follow.\n"
                "   2.3 The system retrieves all triples for the selected anchor, relation and direction. You reason strictly based on them.\n"
                "3. Record conclusions about candidates and choose the next action. Unless the action is stop, also name the next anchor.\n"
                "   The available actions are:\n"
                "   - continue_path: follow the current path further, e.g. explore an entity found in this step.\n"
                "   - switch_candidate: the current candidate is excluded or cannot be verified; continue with another pending candidate.\n"
                "   - backtrack: the current path is not useful; return to an entity from an earlier step and try another relation.\n"
                "   - stop: end exploration and produce the final answer.\n\n"
                "Terms:\n"
                "- Reasoning Step N in the summary is the same as Iteration N.\n"
                "- A candidate is any entity under examination: entities retrieved during exploration "
                "and entities that conclusions are about, including intermediate entities. A candidate is not necessarily an answer. "
                "For example, for 'Which paintings were made by a Spanish painter?', the answers are paintings, "
                "but the painter of a painting is also a candidate when checking whether the painter is Spanish.\n"
                "- Each candidate has a status: pending (not excluded so far) or excluded (verified by the knowledge graph to fail a condition of the user request). "
                "The summary lists candidates by status.\n\n"
                "Rules:\n"
                "- Base your reasoning on the retrieved information.\n"
                "- Always return results in the exact structured schema provided for that step.\n",
            )
        ]
    )


def get_prompt_summarize_reasoning() -> ChatPromptTemplate:
    return ChatPromptTemplate(
        [
            (
                "user",
                "This is a summary of {number_of_steps} reasoning steps completed so far. "
                "It has five sections:\n"
                "- Detailed Reasoning Steps: the anchor and relation of each valid step, the triples it used "
                "(Used Triples) and its implications. "
                "A step discarded as irrelevant has no Used Triples or Implications.\n"
                "- Verified facts: conclusions confirmed by the knowledge graph, with the triples "
                "or the missing relation as evidence.\n"
                "- Unverified assumptions: conclusions not confirmed by the knowledge graph, e.g. based on "
                "background knowledge, a guess or rejected evidence. Do not treat them as facts.\n"
                "- Excluded candidates: candidates verified to fail a condition.\n"
                "- Pending candidates: candidates not excluded so far, grouped by the reasoning step that "
                "retrieved them. They include intermediate entities and entities irrelevant to the request.\n\n"
                "{summary}\n\n"
                "You must use this summary to maintain consistency. Do not repeat facts already retrieved unless needed for clarity.",
            )
        ]
    )


def get_prompt_select_anchor() -> ChatPromptTemplate:
    return ChatPromptTemplate(
        [
            (
                "user",
                "(Iteration {iteration}, Step 2.1, Attempt {attempt}):\n"
                "{action_hint}"
                "{failed_attempts}"
                "Task: Select exactly ONE specific anchor entity (a node name) from the knowledge graph "
                "that is most likely to lead to information for answering the user request.\n"
                "Rules:\n"
                "- Must be an EXACT match to a KG entity name.\n"
                "- Avoid special character changes (e.g., 'Maria de Ventadorn' must NOT become 'Maria_de_Ventadorn').\n"
                "- Copy names from the summary or the list above exactly, including the ID in parentheses if present.\n"
                "- Do not select an excluded candidate to check it again.\n"
                "- If a previous action is shown above, select the planned next anchor unless the summary "
                "shows a reason not to; without a plan, prefer an entity from the list. "
                "Other existing entities are also accepted.\n"
                "Return your answer in the following structured schema:\n{schema}",
            )
        ]
    )


def get_prompt_select_relation() -> ChatPromptTemplate:
    return ChatPromptTemplate(
        [
            (
                "user",
                "(Iteration {iteration}, Step 2.2, Attempt {attempt}):\n"
                "Current anchor entity: {anchor}\n"
                "Available relation-direction pairs for this entity: "
                "{available_relations}\n"
                "{explored_relations}"
                "{summary_previous_attempts}"
                "Task: Select exactly ONE available relation-direction pair "
                "to explore towards answering the user question.\n"
                "Direction is relative to the current anchor:\n"
                "- outgoing: anchor --relation--> another entity.\n"
                "- incoming: another entity --relation--> anchor.\n"
                "Return the exact relation name in 'value', including its "
                "identifier in parentheses if present, and the corresponding "
                "direction in 'direction'. Return a relation name, not an entity name.\n"
                "The relation and direction must occur together in one of "
                "the available pairs above. Do not select 'both'.\n"
                "Incoming traversal does not reverse the fact: retrieved "
                "triples retain their original head, relation, and tail.\n"
                "Any semantically closest relations mentioned in retry feedback "
                "are suggestions from the whole graph; select one only with "
                "a direction listed for it in the available pairs above.\n"
                "Notes:\n"
                "- When returning an empty string as the relation value, "
                "you will be routed back to Step 2.1 to select a new anchor "
                "entity. In this case, set direction to 'outgoing' as a "
                "placeholder and explain your decision in justification. "
                "No triple retrieval will be performed for this empty selection.\n"
                "Return your answer in the following schema:\n{schema}",
            )
        ]
    )


def get_prompt_perform_reasoning() -> ChatPromptTemplate:
    return ChatPromptTemplate(
        [
            (
                "user",
                "(Iteration {iteration}, Step 3, Attempt {attempt})\n"
                "You have received all triples from the KG for the selected anchor, relation and direction.\n"
                "Task: Reason based on these triples towards answering the user request.\n"
                "Rules for keys and discard_step:\n"
                "- keys: the keys of the triples from this step that you use. Select only keys from: {allowed_keys}.\n"
                "- If none of the triples are relevant, set keys to an empty list and discard_step to true. "
                "Discarding a step does not stop exploration.\n"
                "Rules for conclusions:\n"
                "- Add one conclusion for each candidate and condition of the user request that this step informs, "
                "including negative conclusions (the candidate does not satisfy the condition). "
                "Candidates include intermediate entities, not only possible answers.\n"
                "- Write the candidate exactly as it appears in the triples or the summary, including the ID in parentheses if present.\n"
                "- kg_triple: the candidate must appear in the triples whose keys the conclusion lists.\n"
                "- kg_absence: the candidate or the absent_entity must be the anchor of this step, "
                "and the other one must not appear in the triples retrieved in this step.\n"
                "- A judgement that is not based on the triples of this step, e.g. on general knowledge "
                "or on an entity name, must be marked as background or guess.\n"
                "- If the summary already contains the same condition, copy its condition text exactly.\n"
                "Rules for the next action:\n"
                "- If previous reasoning steps exist, integrate them without contradiction.\n"
                "- Entities in these triples and pending candidates in the summary are possible next anchors.\n"
                "- next_anchor: if the action is not stop, name the entity you intend to explore next, "
                "exactly as it appears in the triples or the summary, including the ID in parentheses if present.\n"
                "- Only choose stop if you can fully and unambiguously answer the user request from verified facts, "
                "or no further exploration is possible.\n"
                "Return your answer in the following schema: \n{schema}",
            )
        ]
    )


def get_prompt_create_final_answer() -> ChatPromptTemplate:
    return ChatPromptTemplate(
        [
            (
                "user",
                "It is time to prepare the final answer for the user request: {user_request}\n"
                "The previous reasoning steps were as follows:\n"
                "{reasoning_steps}\n\n"
                "Please answer with a structured output given by the following schema: {schema}\n"
                "Notes on answering based on the question types: {question_type_str}",
            )
        ]
    )


def prompts_to_json(file_path: str):
    """
    Converts the prompts defined in this module to a JSON file.

    Args:
        file_path (str): The path where the JSON file will be saved.
    """

    def extract_messages(prompt: ChatPromptTemplate):
        # Convert the internal message tuples to dicts for JSON, ensuring serializability
        messages = []
        for message in prompt.messages:
            if isinstance(message, SystemMessagePromptTemplate):
                messages.append({"role": "system", "content": message.prompt.template})
            else:
                raise ValueError(f"Unsupported message type: {type(message)}")
        return messages

    prompts = {
        "system_description": {
            "messages": extract_messages(get_prompt_system_description())
        },
        "select_anchor": {"messages": extract_messages(get_prompt_select_anchor())},
        "select_relation": {"messages": extract_messages(get_prompt_select_relation())},
        "perform_reasoning": {
            "messages": extract_messages(get_prompt_perform_reasoning())
        },
        "summarize_reasoning": {
            "messages": extract_messages(get_prompt_summarize_reasoning())
        },
        "create_final_answer": {
            "messages": extract_messages(get_prompt_create_final_answer())
        },
    }
    with open(file_path, "w") as f:
        json.dump(prompts, f, indent=4)
