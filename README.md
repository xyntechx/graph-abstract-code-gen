# A Matter of Representation: Towards Graph-Based Abstract Code Generation

> NeurIPS 2025 Deep Learning for Code (DL4C) Workshop

## Abstract

Most large language models (LLMs) today excel at generating raw, sequential code with minimal abstractions and custom structures. However, there has been little work on graph-based abstract code generation, where significant logic is encapsulated in predefined nodes and execution flow is determined by edges. This is relevant for visual programming languages, and in cases where raw source code is inaccessible to users and LLM training sets. In this work, we propose and evaluate JSON representations for graphs to enable high accuracy graph-based abstract code generation. We evaluate these representations on ScratchTest, a mini-benchmark based on our custom Python re-implementation of Scratch, which tests the LLM in code graph space. Our findings demonstrate that LLMs can indeed perform the aforementioned generation task in a single pass without relying on specialized or complex pipelines, given the correct graph representations. We also show that different representations induce significantly different accuracies, highlighting the instrumental role of representations in this generation task. All in all, this work establishes the first steps towards representation learning for graph-based abstract code generation.

## Running

Create a virtual env and install the dependencies. We recommend `uv`, but `conda` or anything else works too!
```
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Run `main.py`.
```
python main.py -m <model_choice> -r <repr_choice> -t <test_choice>
```

where `model_choice` can be any one of `gpt`, `qwen`, `deepseek`, `llama`;

and `repr_choice` can be any one of `proposed`, `extra_desc`, `no_types`, `alternative`;

and `test_choice` can be any one of `batch_1`, `batch_2`, `batch_3`, `batch_4`.

Note: See `agents.py` for the specific models being used.
