from typing import Any, Literal

from pipelex.core.stuffs.stuff_content import StructuredContent
from pipelex.libraries.pipelines.builder.pipe.pipe_signature import PipeSpec
from pipelex.pipe_operators.compose.pipe_compose_blueprint import PipeComposeBlueprint
from pipelex.tools.templating.jinja2_template_category import Jinja2TemplateCategory
from pipelex.tools.templating.templating_models import PromptingStyle, TagStyle, TextFormat
from pydantic import Field
from typing_extensions import override


class PromptingStyleSpec(StructuredContent):
    tag_style: TagStyle = Field(strict=False)
    text_format: TextFormat = Field(TextFormat.PLAIN, strict=False)


class PipeComposeSpec(PipeSpec):
    type: Literal["PipeCompose"] = "PipeCompose"
    category: Literal["PipeOperator"] = "PipeOperator"
    the_pipe_code: str = Field(description="Pipe code. Must be snake_case.")
    jinja2_name: str | None = Field(default=None, description="Name of the Jinja2 template to use")
    jinja2: str | None = Field(default=None, description="Raw Jinja2 template string")
    prompting_style: PromptingStyleSpec | None = Field(default=None, description="Style of prompting to use (typically for different LLMs)")
    template_category: Jinja2TemplateCategory = Field(
        default=Jinja2TemplateCategory.LLM_PROMPT,
        description="Category of the template (could also be HTML, MARKDOWN, MERMAID, etc.), influences Jinja2 rendering environment config",
    )
    extra_context: dict[str, Any] | None = Field(default=None, description="Additional context variables for template rendering")

    @override
    def to_blueprint(self) -> PipeComposeBlueprint:
        base_blueprint = super().to_blueprint()

        if self.prompting_style:
            prompting_style = (
                self.prompting_style
                if isinstance(self.prompting_style, PromptingStyle)
                else PromptingStyle(tag_style=self.prompting_style.tag_style, text_format=self.prompting_style.text_format)
            )
        else:
            prompting_style = None

        return PipeComposeBlueprint(
            definition=base_blueprint.definition,
            inputs=base_blueprint.inputs,
            output=base_blueprint.output,
            type=self.type,
            category=self.category,
            jinja2_name=self.jinja2_name,
            jinja2=self.jinja2,
            prompting_style=prompting_style,
            template_category=self.template_category,
            extra_context=self.extra_context,
        )
