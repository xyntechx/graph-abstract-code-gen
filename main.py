import json
import subprocess
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
from argparse import ArgumentParser

from scratch import *
from agents import agent_no_types, agent_proposed, agent_alternative, agent_extra_desc
from utils import (
    topological_sort,
    get_arg_val,
    get_substack_blocks,
    get_substackelse_blocks,
    convert_repr,
    get_reference_proposed,
)


def pipeline(repr_choice, model_choice, query, filepath, logpath):
    try:
        match repr_choice:
            case "proposed":
                graph = json.loads(agent_proposed(query, model_choice))
            case "extra_desc":
                graph = json.loads(agent_extra_desc(query, model_choice))
            case "no_types":
                graph = json.loads(agent_no_types(query, model_choice))
            case "alternative":
                graph_raw = json.loads(agent_alternative(query, model_choice))
                graph = convert_repr(graph_raw, get_reference_proposed())

        ordered_ids = topological_sort(graph)

        with open(logpath, "a") as f:
            f.write(f"{json.dumps(graph, indent=2)}\n\n")

        has_substack, has_substack_else = [], []

        program = []

        program.append("import sys")
        program.append("import os")
        program.append(
            "project_root = os.path.join(os.path.dirname(__file__), '../../../')"
        )
        program.append("resolved_path = os.path.abspath(project_root)")
        program.append("sys.path.append(resolved_path)")
        program.append("from scratch import *")
        program.append("program = ScratchProgram()")

        # Create blocks
        for id in ordered_ids:
            name = graph["nodes"][id]["name"]
            if name == "Constant":
                val = graph["nodes"][id]["value"]
                if isinstance(val, str):
                    program.append(f"{id} = '{val}'")
                else:
                    program.append(f"{id} = {val}")
                continue

            params = []
            ins, fields = REF[name]["inPorts"], REF[name]["fields"]
            ports = ins + fields
            for port in ports:
                port_id = port["id"]
                if port_id == "EXEC":
                    continue
                params.append(
                    f"{port_id.lower()}={get_arg_val(id, port_id, graph['edges'])}"
                )

            outs = REF[name]["outPorts"]
            for port in outs:
                port_id = port["id"]
                if port_id == "SUBSTACK" or port_id == "SUBSTACK_IF":
                    has_substack.append(id)
                elif port_id == "SUBSTACK_ELSE":
                    has_substack_else.append(id)

            program.append(f"{id} = {name}Block({', '.join(params)})")

        # Add substacks
        for id in has_substack:
            blocks = get_substack_blocks(id, graph["edges"])
            for block in blocks:
                program.append(f"{id}.add_to_substack({block})")

        for id in has_substack_else:
            blocks = get_substackelse_blocks(id, graph["edges"])
            for block in blocks:
                program.append(f"{id}.add_to_else_substack({block})")

        # Connect blocks
        for e in graph["edges"]:
            if e["outPortID"] == "THEN" and e["inPortID"] == "EXEC":
                program.append(f"{e['outNodeID']}.connect_next({e['inNodeID']})")

        # Add script to program
        for id in ordered_ids:
            name = graph["nodes"][id]["name"]
            if name == "WhenFlagClicked" or name == "WhenKeyPressed":
                program.append(f"program.add_script({id})")
                break

        # Execute program
        program.append("results, final_context = program.execute()")

        program.append(f"with open('{logpath}', 'a') as f:")
        program.append("    f.write(f'{results}')")
        program.append(f"with open('{logpath}', 'a') as f:")
        program.append("    f.write(f'{final_context}')")

        with open(filepath, "w") as f:
            program_str = "\n".join(program)
            f.write(program_str)

    except Exception as e:
        error_message = f"GRAPH GEN ERROR: {filepath} is thus empty. {e}"
        print(error_message)
        with open(logpath, "w") as f:
            f.write(error_message)
        with open(filepath, "w") as f:
            f.write("")


def get_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-m",
        "--model",
        dest="model",
        required=True,
        choices=["gpt", "qwen", "deepseek", "llama"],
    )
    parser.add_argument(
        "-r",
        "--repr",
        dest="repr",
        required=True,
        choices=["proposed", "extra_desc", "no_types", "alternative"],
    )
    parser.add_argument(
        "-t",
        "--test",
        dest="test",
        required=True,
        choices=["batch_1", "batch_2", "batch_3", "batch_4"],
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_args()

    REF = get_reference_proposed()

    with open(f"tests/{args.test}.txt") as f:
        queries = f.read().strip().split("\n")

    today = datetime.now()
    timestamp = f"{today.year}{today.month:02}{today.day:02}{today.hour:02}{today.minute:02}{today.second:02}"
    dir = Path(f"out/{args.repr}-{args.model}-{args.test}-{timestamp}")

    for i in tqdm(range(len(queries))):
        dirr = dir / f"{i+1}"
        dirr.mkdir(parents=True, exist_ok=True)

        filepath = dirr / f"out.py"
        logpath = dirr / f"log.txt"

        pipeline(args.repr, args.model, queries[i], filepath, logpath)

    for i in tqdm(range(len(queries))):
        filepath = dir / f"{i+1}" / f"out.py"
        subprocess.run(["python", filepath])

    print(f"Results saved in {dir}")
