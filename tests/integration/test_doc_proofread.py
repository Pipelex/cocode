import pytest
from pipelex.core.memory.working_memory_factory import WorkingMemoryFactory
from pipelex.core.stuffs.list_content import ListContent
from pipelex.core.stuffs.stuff_factory import StuffFactory
from pipelex.interpreter_hub import get_required_concept
from pipelex.pipeline.runner import PipelexMTHDSProtocol
from pipelex.system.pipe_run_mode import PipeRunMode

from cocode.pipelines.doc_proofread.doc_proofread_models import (
    DocumentationFile,
    DocumentationFileInconsistencies,
    DocumentationInconsistency,
    RepositoryMap,
)


@pytest.mark.asyncio(loop_scope="class")
class TestDocProofread:
    async def test_all_inconsistencies_is_one_flat_list(self) -> None:
        """A dry run over several documentation files stores every inconsistency in one flat list, as the report step reads it."""
        doc_files = [
            DocumentationFile(file_path=f"docs/page_{index_doc}.md", doc_content=f"# Page {index_doc}\n\nCall `foo()`.", title=f"Page {index_doc}")
            for index_doc in range(2)
        ]
        working_memory = WorkingMemoryFactory.make_from_multiple_stuffs(
            stuff_list=[
                StuffFactory.make_stuff(
                    concept=get_required_concept(concept_ref="doc_proofread.RepositoryMap"),
                    content=RepositoryMap(repo_content="src/foo.py\ndef foo(): ..."),
                    name="repo_map",
                ),
                StuffFactory.make_stuff(
                    concept=get_required_concept(concept_ref="doc_proofread.DocumentationFile"),
                    content=ListContent[DocumentationFile](items=doc_files),
                    name="doc_files",
                ),
            ]
        )

        response = await PipelexMTHDSProtocol(pipe_run_mode=PipeRunMode.DRY).execute(pipe_code="doc_proofread", inputs=working_memory)
        output_memory = response.pipe_output.working_memory

        inconsistencies_by_doc_file = output_memory.get_stuff_as_list("inconsistencies_by_doc_file", item_type=DocumentationFileInconsistencies)
        assert len(inconsistencies_by_doc_file.items) == len(doc_files)
        expected_inconsistencies = [
            inconsistency
            for doc_file_inconsistencies in inconsistencies_by_doc_file.items
            for inconsistency in doc_file_inconsistencies.inconsistencies
        ]
        # The dry run's mocks fill each file's list, so the comparison below has items to compare.
        assert expected_inconsistencies

        # Reading the items as inconsistencies refuses a list in their place, which a batch over a list-producing pipe stores.
        all_inconsistencies = output_memory.get_stuff_as_list("all_inconsistencies", item_type=DocumentationInconsistency)
        assert all_inconsistencies.items == expected_inconsistencies
