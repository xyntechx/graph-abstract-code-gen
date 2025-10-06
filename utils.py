import json
from collections import defaultdict, deque


def topological_sort(graph_data):
    nodes = graph_data["nodes"]
    edges = graph_data["edges"]

    adj_list = defaultdict(list)
    in_degree = defaultdict(int)

    for node_id in nodes:
        in_degree[node_id] = 0

    for edge in edges:
        out_node = edge["outNodeID"]
        in_node = edge["inNodeID"]

        adj_list[out_node].append(in_node)
        in_degree[in_node] += 1

    queue = deque()
    for node_id in nodes:
        if in_degree[node_id] == 0:
            queue.append(node_id)

    result = []

    while queue:
        current = queue.popleft()
        result.append(current)

        for neighbor in adj_list[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(nodes):
        raise ValueError("Error: Graph is not a DAG")

    return result


def convert_repr(agent_b_graph, node_reference):
    agent_a_graph = {"nodes": {}, "edges": []}

    for node_id, node_data in agent_b_graph.items():
        agent_a_graph["nodes"][node_id] = {
            "name": node_data["nodeName"],
            "value": node_data.get("value", None),
        }

    processed_edge_pairs = set()

    for node_id, node_data in agent_b_graph.items():
        node_name = node_data["nodeName"]

        if node_name not in node_reference and node_name != "Constant":
            continue

        for edge in node_data.get("edges", []):
            port_id = edge["portID"]
            other_node_id = edge["otherNodeID"]
            other_node_data = agent_b_graph[other_node_id]
            other_node_name = other_node_data["nodeName"]

            other_port_id = ""
            for other_edge in other_node_data.get("edges", []):
                if other_edge["otherNodeID"] == node_id:
                    other_port_id = other_edge["portID"]
                    break

            connection_id = tuple(
                sorted([(node_id, port_id), (other_node_id, other_port_id)])
            )

            if connection_id in processed_edge_pairs:
                continue

            processed_edge_pairs.add(connection_id)

            if node_name == "Constant":
                out_node_id, out_port_id, in_node_id, in_port_id = (
                    node_id,
                    "",
                    other_node_id,
                    other_port_id,
                )
            elif other_node_name == "Constant":
                out_node_id, out_port_id, in_node_id, in_port_id = (
                    other_node_id,
                    "",
                    node_id,
                    port_id,
                )
            else:
                node1_schema = node_reference.get(node_name, {})
                node2_schema = node_reference.get(other_node_name, {})

                out_ports = node1_schema.get("outPorts", [])
                node1_port_is_output = any(port["id"] == port_id for port in out_ports)

                in_ports = node2_schema.get("inPorts", [])
                fields = node2_schema.get("fields", [])
                node2_port_is_input = any(
                    port["id"] == other_port_id for port in in_ports
                ) or any(field["id"] == other_port_id for field in fields)

                if node1_port_is_output and node2_port_is_input:
                    out_node_id, out_port_id, in_node_id, in_port_id = (
                        node_id,
                        port_id,
                        other_node_id,
                        other_port_id,
                    )
                else:
                    out_ports_2 = node2_schema.get("outPorts", [])
                    node2_port_is_output = any(
                        port["id"] == other_port_id for port in out_ports_2
                    )

                    in_ports_1 = node1_schema.get("inPorts", [])
                    fields_1 = node1_schema.get("fields", [])
                    node1_port_is_input = any(
                        port["id"] == port_id for port in in_ports_1
                    ) or any(field["id"] == port_id for field in fields_1)

                    if node2_port_is_output and node1_port_is_input:
                        out_node_id, out_port_id, in_node_id, in_port_id = (
                            other_node_id,
                            other_port_id,
                            node_id,
                            port_id,
                        )
                    else:
                        raise ValueError(
                            f"Could not determine edge direction between {node_name}.{port_id if port_id else 'undefined'} and {other_node_name}.{other_port_id if other_port_id else 'undefined'}"
                        )

            agent_a_edge = {
                "outNodeID": out_node_id,
                "outPortID": out_port_id,
                "inNodeID": in_node_id,
                "inPortID": in_port_id,
            }

            agent_a_graph["edges"].append(agent_a_edge)

    return agent_a_graph


def get_reference_proposed():
    with open("ref-nodes/proposed.json") as f:
        reference = json.load(f)
    return reference


def get_reference_extra_desc():
    with open("ref-nodes/extra-desc.json") as f:
        reference = json.load(f)
    return reference


def get_reference_no_types():
    with open("ref-nodes/no-types.json") as f:
        reference = json.load(f)
    return reference


def get_arg_val(id, port_id, edges):
    for e in edges:
        if e["inNodeID"] == id and e["inPortID"] == port_id:
            return e["outNodeID"]


def get_substack_blocks(id, edges):
    blocks = []
    for e in edges:
        if e["outNodeID"] == id and (
            e["outPortID"] == "SUBSTACK" or e["outPortID"] == "SUBSTACK_IF"
        ):
            blocks.extend(get_execution_chain(e["inNodeID"], edges))
    return blocks


def get_substackelse_blocks(id, edges):
    blocks = []
    for e in edges:
        if e["outNodeID"] == id and e["outPortID"] == "SUBSTACK_ELSE":
            blocks.extend(get_execution_chain(e["inNodeID"], edges))
    return blocks


def get_execution_chain(id, edges):
    exec_map = {}

    for conn in edges:
        if conn["outPortID"] == "THEN" and conn["inPortID"] == "EXEC":
            exec_map[conn["outNodeID"]] = conn["inNodeID"]

    chain = []
    current_node = id
    visited = set()

    while current_node is not None and current_node not in visited:
        chain.append(current_node)
        visited.add(current_node)
        current_node = exec_map.get(current_node)

    return chain
