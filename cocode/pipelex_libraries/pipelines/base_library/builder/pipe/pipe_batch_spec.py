from typing import Literal

from pipelex.libraries.pipelines.builder.pipe.pipe_signature import PipeSpec
from pipelex.pipe_controllers.batch.pipe_batch_blueprint import PipeBatchBlueprint
from pydantic import Field
from typing_extensions import override


class PipeBatchSpec(PipeSpec):
    """Spec for batch processing pipe operations in the Pipelex framework.

    PipeBatch enables parallel execution of a single pipe across multiple items
    in a list. Each item is processed independently, making it ideal for data
    transformation, enrichment, or analysis tasks on collections.

    This controller is commonly used within PipeSequence for inline batch processing,
    where the batch configuration is specified directly in the sequence step using
    batch_over and batch_as parameters in SubPipeBlueprint.

    Attributes:
        the_pipe_code: Pipe code. Must be snake_case.
        type: Fixed to "PipeBatch" for this pipe type.
        branch_pipe_code: The pipe code to execute for each item in the input list.
                         This pipe is instantiated once per item in parallel.
        input_list_name: Name of the list in WorkingMemory to iterate over.
                        Defaults to the PipeBatch's main input name if not specified.
        input_item_name: Name assigned to individual items within each execution branch.
                        This is how the branch pipe accesses its specific input item.

    Validation Rules:
        1. branch_pipe_code must reference an existing pipe in the pipeline.
        2. When input_list_name is specified, it must reference a list in context.
        3. The branch pipe should be designed to process single items.

    """

    type: Literal["PipeBatch"] = "PipeBatch"
    category: Literal["PipeController"] = "PipeController"
    the_pipe_code: str = Field(description="Pipe code. Must be snake_case.")
    branch_pipe_code: str
    input_list_name: str | None = None
    input_item_name: str | None = None

    @override
    def to_blueprint(self) -> PipeBatchBlueprint:
        base_blueprint = super().to_blueprint()
        return PipeBatchBlueprint(
            definition=base_blueprint.definition,
            inputs=base_blueprint.inputs,
            output=base_blueprint.output,
            type=self.type,
            category=self.category,
            branch_pipe_code=self.branch_pipe_code,
            input_list_name=self.input_list_name,
            input_item_name=self.input_item_name,
        )
