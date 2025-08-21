import re
from typing import Dict, List, Set

from pipelex.core.memory.working_memory import WorkingMemory
from pipelex.core.stuffs.stuff_content import ListContent, StructuredContent, TextContent
from pipelex.tools.func_registry import func_registry
from pydantic import Field


class TextChunk(StructuredContent):
    """A chunk of text that is part of a larger text."""

    chunk_text: str = Field(..., description="The text content of this chunk")
    chunk_index: int = Field(..., description="The index of this chunk in the original text")
    start_position: int = Field(..., description="Starting character position in the original text")
    end_position: int = Field(..., description="Ending character position in the original text")


def split_text_by_identifiers(working_memory: WorkingMemory) -> ListContent[TextChunk]:
    """
    Split `text` into chunks using the *first* full-line occurrence of every
    identifier in `split_identifiers`.

    * A delimiter is recognised only when it starts a line (^\\s*<ident>).
    * Subsequent appearances of the same delimiter are ignored.
    """
    large_text: str = working_memory.get_stuff_as_str("text")

    # Pull the identifiers as plain strings
    id_stuff = working_memory.get_stuff_as_list("split_identifiers", item_type=TextContent)
    identifiers: List[str] = [d.text.strip() for d in id_stuff.items if d.text.strip()]

    # Safety: no ids → one big chunk
    if not identifiers:
        return ListContent(items=[TextChunk(chunk_text=large_text, chunk_index=0, start_position=0, end_position=len(large_text))])

    # --------------------------------------------------------------------- #
    # 1️⃣  Find *first* position of each identifier as a full-line prefix
    # --------------------------------------------------------------------- #
    split_positions: Dict[int, str] = {}  # pos → delimiter
    seen: Set[str] = set()  # dedupe

    for ident in identifiers:
        if ident in seen:
            continue
        seen.add(ident)

        # Regex: delimiters may be indented (git diff lines often start with "+", "-" etc.)
        pattern = re.compile(rf"(?m)^[^\S\r\n]*{re.escape(ident)}")
        match = pattern.search(large_text)
        if match:
            split_positions[match.start()] = ident

    # Nothing matched → one big chunk
    if not split_positions:
        return ListContent(items=[TextChunk(chunk_text=large_text, chunk_index=0, start_position=0, end_position=len(large_text))])

    # --------------------------------------------------------------------- #
    # 2️⃣  Build chunks from the ordered split positions
    # --------------------------------------------------------------------- #
    chunks: List[TextChunk] = []
    current_start = 0
    for idx, pos in enumerate(sorted(split_positions)):
        # Skip empty regions (e.g. two delimiters right after each other)
        if pos <= current_start:
            continue
        chunks.append(TextChunk(chunk_text=large_text[current_start:pos], chunk_index=idx, start_position=current_start, end_position=pos))
        current_start = pos

    # Trailing chunk
    if current_start < len(large_text):
        chunks.append(
            TextChunk(chunk_text=large_text[current_start:], chunk_index=len(chunks), start_position=current_start, end_position=len(large_text))
        )

    return ListContent(items=chunks)


func_registry.register_function(split_text_by_identifiers, name="split_text_by_identifiers")
