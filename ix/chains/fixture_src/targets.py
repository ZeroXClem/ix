EMBEDDINGS_TARGET = {
    "key": "embeddings",
    "type": "target",
    "source_type": "embedding",
}


LLM_TARGET = {
    "key": "llm",
    "type": "target",
    "source_type": "llm",
}

MEMORY_BACKEND_TARGET = {
    "key": "chat_memory",
    "type": "target",
    "source_type": "memory_backend",
}

OUTPUT_PARSER_TARGET = {
    "key": "output_parser",
    "type": "target",
    "source_type": "output_parser",
}

PROMPT_TARGET = {
    "key": "prompt",
    "type": "target",
    "source_type": "prompt",
}

MEMORY_TARGET = {
    "key": "memory",
    "type": "target",
    "source_type": "memory",
    "multiple": True,
}

SEQUENCE_CHAINS_TARGET = {
    "key": "chains",
    "type": "target",
    "source_type": "chain",
    "auto_sequence": False,
}

CHAIN_TARGET = {
    "key": "chain",
    "type": "target",
    "source_type": "chain",
}

FUNCTION_TARGET = {
    "key": "functions",
    "type": "target",
    "source_type": "tool",
    "multiple": True,
}

OUTPUT_PARSER_TARGET = {
    "key": "output_parser",
    "type": "target",
    "source_type": "output_parser",
}

VECTORSTORE_TARGET = {
    "key": "vectorstore",
    "type": "target",
    "source_type": "vectorstore",
}
