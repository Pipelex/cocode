from typing import Literal

from pipelex.libraries.pipelines.builder.pipe.pipe_signature import PipeSpec
from pipelex.pipe_operators.ocr.pipe_ocr_blueprint import PipeOcrBlueprint
from pipelex.types import StrEnum
from pydantic import Field
from typing_extensions import override


class RecommendedOcrPreset(StrEnum):
    BASE_OCR_MISTRAL = "base_ocr_mistral"
    BASE_OCR_PYPDFIUM2 = "base_ocr_pypdfium2"


class PipeOcrSpec(PipeSpec):
    """Spec for OCR (Optical Character Recognition) pipe operations in the Pipelex framework.

    PipeOcr enables text extraction from images and documents using OCR technology.
    Supports various OCR platforms and output configurations including image detection,
    caption generation, and page rendering.

    VERY IMPORTANT: THE INPUT OF THE PIPEOCR MUST BE either an image or a pdf or a concept which refines one of them.

    Attributes:
        the_pipe_code: Pipe code. Must be snake_case.
        type: Fixed to "PipeOcr" for this pipe type.
        ocr: name of the OCR model or handle or preset or setting
        page_images: Whether to include detected images in the OCR output. When enabled,
                    extracts and returns embedded images found in documents.
        page_image_captions: Whether to generate captions for detected images using AI.
                            Useful for understanding image content in documents.
        page_views: Whether to include rendered page views in the output. Provides
                   visual representation of document pages.
        page_views_dpi: DPI (dots per inch) resolution for rendered page views.
                       Higher values provide better quality but larger file sizes.
                       Defaults to configuration setting.
    """

    type: Literal["PipeOcr"] = "PipeOcr"
    category: Literal["PipeOperator"] = "PipeOperator"
    the_pipe_code: str = Field(description="Pipe code. Must be snake_case.")
    ocr: RecommendedOcrPreset | str = Field(description="Use one of the recommended OCR presets")
    page_images: bool | None = None
    page_image_captions: bool | None = None
    page_views: bool | None = None
    page_views_dpi: int | None = None

    @override
    def to_blueprint(self) -> PipeOcrBlueprint:
        base_blueprint = super().to_blueprint()

        return PipeOcrBlueprint(
            definition=base_blueprint.definition,
            inputs=base_blueprint.inputs,
            output=base_blueprint.output,
            type=self.type,
            category=self.category,
            ocr=self.ocr,
        )
