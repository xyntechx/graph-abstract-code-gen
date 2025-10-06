import json
from dotenv import dotenv_values
from groq import Groq
from utils import (
    get_reference_extra_desc,
    get_reference_proposed,
    get_reference_no_types,
)


config = dotenv_values(".env")
client = Groq(api_key=config["GROQ_API_KEY"])


SYSTEM_F = (
    lambda ref: f"""## Goal

You are an expert software engineer extremely proficient in programming using a graph-based, visual programming language. You will be provided with the following information:

**User Query**: The overall functionality that you are required to fulfill through calling pre-declared functions.

Your task is to analyze the **User Query** and generate a connected graph that fulfills the requested functionality in **User Query**. All necessary nodes and connections MUST be included in your output. Each node can be instantiated in the graph more than once.

## Node Reference (Complete Form)

Every possible node in their complete form:
{ref}

## Output Format

Your output must be a JSON object in the following format:
{'{"nodes": Dict[str, Node], "edges": List[Edge]}'}

The keys of the `nodes` dictionary are NODEIDs, which are unique string identifiers such that no two nodes can have the same NODEID. A NODEID must contain only letters (a-z, A-Z) and be prefixed with 'node_'.

The Node type is
{'{"name": NODENAME, "value": any|None}'}
The value field of a Node type is always None except for when it is for a constant, in which case its NODENAME is "Constant" and its value is the value it is supposed to hold (e.g. 10, "Hello", True).

The Edge type is
{'{"outNodeID": str, "outPortID": str, "inNodeID": str, "inPortID": str}'}
outNodeID is the NODEID of the node of which you are using one of the outPorts. inNodeID is the NODEID of the node of which you are using one of the inPorts. Connecting constants to a node should be done like the following example: 'moving 10 steps' means having the edge {'{"outNodeID": IDOfAConstantNode, "outPortID": "", "inNodeID": "IDOfAMoveStepsNode", "inPortID": "STEPS"}'}. A `field` of a node can be considered an inPort for the purposes of an Edge. An outPort connects to an inPort; an outPort cannot connect to another outPort, and an inPort cannot connect to another inPort."""
)


SYSTEM_ALT_F = (
    lambda ref: f"""## Goal

You are an expert software engineer extremely proficient in programming using a graph-based, visual programming language. You will be provided with the following information:

**User Query**: The overall functionality that you are required to fulfill through calling pre-declared functions.

Your task is to analyze the **User Query** and generate a connected graph that fulfills the requested functionality in **User Query**. All necessary nodes and connections MUST be included in your output. Each node can be instantiated in the graph more than once.

## Node Reference (Complete Form)

Every possible node in their complete form:
{ref}

## Output Format

Your output must be a JSON object in the following format:
{'{[key: NODEID]: {"nodeName": NODENAME, "value": any|None, "edges": List[Edge]}}'}

NODEIDs are unique string identifiers such that no two nodes can have the same NODEID. A NODEID must contain only letters (a-z, A-Z) and be prefixed with 'node_'. The value field of a Node type is always None except for when it is for a constant, in which case its NODENAME is "Constant" and its value is the value it is supposed to hold (e.g. 10, "Hello", True).

The Edge type is
{'{"portID": str, "otherNodeID": OTHERNODEID}'}

OTHERNODEID is the NODEID this current node is connected to via the port with id that matches the one specified in portID. An outPort connects to an inPort; an outPort cannot connect to another outPort, and an inPort cannot connect to another inPort. A Constant node has only one port, and it is an outPort: VALUE. A `field` of a node can be considered an inPort for the purposes of an Edge. Port connections must be defined in the `edges` list for both the to and from nodes."""
)

MODEL_MAP = {
    "gpt": "openai/gpt-oss-120b",
    "qwen": "qwen/qwen3-32b",
    "deepseek": "deepseek-r1-distill-llama-70b",
    "llama": "llama-3.3-70b-versatile",
}

REASONING_MAP = {
    "gpt": "medium",
    "qwen": "default",
    "deepseek": None,
    "llama": None,
}


def agent_proposed(query: str, model_choice: str) -> str:
    user_message = f"**User Query**: {query}"

    REF = get_reference_proposed()

    SYSTEM = SYSTEM_F(json.dumps(REF, indent=2))

    completion = client.chat.completions.create(
        model=MODEL_MAP[model_choice],
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_message},
        ],
        temperature=1,
        max_completion_tokens=8192,
        top_p=1,
        reasoning_effort=REASONING_MAP[model_choice],
        stream=False,
        response_format={"type": "json_object"},
        stop=None,
    )

    return completion.choices[0].message.content


def agent_no_types(query: str, model_choice: str) -> str:
    user_message = f"**User Query**: {query}"

    REF = get_reference_no_types()

    SYSTEM = SYSTEM_F(json.dumps(REF, indent=2))

    completion = client.chat.completions.create(
        model=MODEL_MAP[model_choice],
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_message},
        ],
        temperature=1,
        max_completion_tokens=8192,
        top_p=1,
        reasoning_effort=REASONING_MAP[model_choice],
        stream=False,
        response_format={"type": "json_object"},
        stop=None,
    )

    return completion.choices[0].message.content


def agent_extra_desc(query: str, model_choice: str) -> str:
    user_message = f"**User Query**: {query}"

    REF = get_reference_extra_desc()

    SYSTEM = SYSTEM_F(json.dumps(REF, indent=2))

    completion = client.chat.completions.create(
        model=MODEL_MAP[model_choice],
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_message},
        ],
        temperature=1,
        max_completion_tokens=8192,
        top_p=1,
        reasoning_effort=REASONING_MAP[model_choice],
        stream=False,
        response_format={"type": "json_object"},
        stop=None,
    )

    return completion.choices[0].message.content


def agent_alternative(query: str, model_choice: str) -> str:
    user_message = f"**User Query**: {query}"

    REF = get_reference_proposed()

    SYSTEM = SYSTEM_ALT_F(json.dumps(REF, indent=2))

    completion = client.chat.completions.create(
        model=MODEL_MAP[model_choice],
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_message},
        ],
        temperature=1,
        max_completion_tokens=8192,
        top_p=1,
        reasoning_effort=REASONING_MAP[model_choice],
        stream=False,
        response_format={"type": "json_object"},
        stop=None,
    )

    return completion.choices[0].message.content
