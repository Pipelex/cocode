from datetime import datetime
from typing import Any, cast

from pipelex.core.concepts.concept_blueprint import (
    ConceptBlueprint,
    ConceptBlueprintError,
    ConceptStructureBlueprint,
    ConceptStructureBlueprintError,
    ConceptStructureBlueprintFieldType,
)
from pipelex.core.concepts.concept_native import NativeConceptEnum, NativeConceptManager
from pipelex.core.concepts.exceptions import ConceptCodeError, ConceptStringError, ConceptStringOrConceptCodeError
from pipelex.core.domains.domain import SpecialDomain
from pipelex.core.domains.domain_blueprint import DomainBlueprint
from pipelex.core.memory.working_memory import WorkingMemory
from pipelex.core.stuffs.stuff_content import StructuredContent
from pipelex.tools.misc.string_utils import is_pascal_case
from pipelex.types import Self, StrEnum
from pydantic import ConfigDict, Field, field_validator, model_validator


class ConceptStructureSpecFieldType(StrEnum):
    TEXT = "text"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    NUMBER = "number"
    DATE = "date"


class ConceptSpecError(Exception):
    pass


class ConceptStructureSpec(StructuredContent):
    """Spec defining a field in the structure of a concept, used as a Pydantic V2 model.

    This class represents the schema for a single field in a concept's structure. It supports
    various field types including text, list, dict, integer, boolean, number, and date, as well
    as choice-based fields (enums).

    Attributes:
        the_field_name: Field name. Must be snake_case.
        definition: Natural language description of the field's purpose and usage.
        type: The field's data type.
        required: Whether the field is mandatory. Defaults to True unless explicitly set to False.
        default_value: Default value for the field. Must match the specified type, and for choice
                      fields must be one of the valid choices. When provided, type must be specified
                      (unless choices are provided).

    Validation Rules:
        3. Default values: When default_value is provided:
           - For typed fields: type must be specified and default_value must match that type
           - Type validation includes: text (str), integer (int), boolean (bool),
             number (int/float), dict (dict)

    """

    the_field_name: str = Field(description="Field name. Must be snake_case.")
    definition: str
    type: ConceptStructureSpecFieldType | None = Field(default=None, description="The type of the field.")
    required: bool | None = True
    default_value: Any | None = None

    @model_validator(mode="after")
    def validate_structure_blueprint(self) -> Self:
        """Validate the structure blueprint according to type rules."""
        # Check default_value type is the same as type
        if self.default_value is not None and self.type is not None:
            self._validate_default_value_type()
        return self

    def _validate_default_value_type(self) -> None:
        """Validate that default_value matches the specified type."""
        if self.default_value is None:
            return

        match self.type:
            case None:
                return
            case ConceptStructureSpecFieldType.TEXT:
                if not isinstance(self.default_value, str):
                    self._raise_type_mismatch_error("str", type(self.default_value).__name__)
            case ConceptStructureSpecFieldType.INTEGER:
                if not isinstance(self.default_value, int):
                    self._raise_type_mismatch_error("int", type(self.default_value).__name__)
            case ConceptStructureSpecFieldType.BOOLEAN:
                if not isinstance(self.default_value, bool):
                    self._raise_type_mismatch_error("bool", type(self.default_value).__name__)
            case ConceptStructureSpecFieldType.NUMBER:
                if not isinstance(self.default_value, (int, float)):
                    self._raise_type_mismatch_error("number (int or float)", type(self.default_value).__name__)
            case ConceptStructureSpecFieldType.DATE:
                if not isinstance(self.default_value, datetime):
                    self._raise_type_mismatch_error("date", type(self.default_value).__name__)

    def _raise_type_mismatch_error(self, expected_type_name: str, actual_type_name: str) -> None:
        msg = f"default_value type mismatch: expected {expected_type_name} for type '{self.type}', but got {actual_type_name}"
        raise ConceptStructureBlueprintError(msg)

    def to_blueprint(self) -> ConceptStructureBlueprint:
        # Convert the type enum value - self.type is already a ConceptStructureBlueprintFieldType enum
        # We need to get the corresponding value in the core enum
        core_type = None
        if self.type is not None:
            # Get the string value and use it to get the core enum value
            core_type = ConceptStructureBlueprintFieldType(self.type)

        return ConceptStructureBlueprint(
            definition=self.definition,
            type=core_type,
            required=self.required,
            default_value=self.default_value,
        )


class ConceptSpecDraft(StructuredContent):
    the_concept_code: str = Field(description="Concept code. Must be PascalCase.")
    definition: str = Field(description="Description of the concept, in natural language.")
    structure: str = Field(
        description="A description of a dict with fieldnames as keys, and values being a dict with: definition, type, required, default_value",
    )
    refines: str | None = Field(
        default=None,
        description="The native concept this concept extends (Text, Image, PDF, TextAndImages, Number, Page) "
        "in PascalCase format. Cannot be used together with 'structure'.",
    )


class ConceptSpec(StructuredContent):
    """Spec defining a concept that can be used in the Pipelex framework.

    A concept represents a structured data type that can either define its own structure
    or refine an existing native concept. Concepts are fundamental building blocks in
    Pipelex workflows for data validation and transformation.

    Attributes:
        the_concept_code: Concept code. Must be PascalCase.
        definition: Natural language description of what the concept represents and its purpose.
        structure: The concept's field structure. Can be either:
                  - A string referring to another concept
                  - A dictionary where keys are field names (in snake_case) and values are
                    either strings (concept references) or ConceptStructureBlueprint instances
                  Cannot be used together with 'refines'.
        refines: The native concept this concept extends (Text, Image, PDF, TextAndImages,
                Number, Page) in PascalCase format. Cannot be used together with 'structure'.

    Validation Rules:
        1. Mutual exclusivity: A concept must have either 'structure' or 'refines', but not both.
        2. Field names: When structure is a dict, all keys must be valid snake_case identifiers.
        3. Concept codes: Must be in PascalCase format (letters and numbers only, starting
           with uppercase, no dots).
        4. Concept strings: Format is "domain.ConceptCode" where domain is lowercase and
           ConceptCode is PascalCase.
        5. Native concepts: When refining, must be one of the valid native concepts.
        6. Structure values: In structure dict, values must be either valid concept strings
           or ConceptStructureBlueprint instances.

    """

    model_config = ConfigDict(extra="forbid")

    the_concept_code: str = Field(description="Concept code. Must be PascalCase.")
    definition: str
    structure: str | dict[str, str | ConceptStructureSpec] | None = None
    refines: str | None = None

    @classmethod
    def is_native_concept_code(cls, concept_code: str) -> bool:
        ConceptSpec.validate_concept_code(concept_code=concept_code)
        return concept_code in NativeConceptEnum.values_list()

    @classmethod
    def validate_concept_code(cls, concept_code: str) -> None:
        if not is_pascal_case(concept_code):
            msg = f"Concept code '{concept_code}' must be PascalCase (letters and numbers only, starting with uppercase, without `.`)"
            raise ConceptCodeError(msg)

    @classmethod
    def validate_concept_string_or_code(cls, concept_string_or_code: str) -> None:
        if concept_string_or_code.count(".") > 1:
            msg = (
                f"concept_string_or_code '{concept_string_or_code}' is invalid. "
                "It should either contain a domain in snake_case and a concept code in PascalCase separated by one dot, "
                "or be a concept code in PascalCase."
            )
            raise ConceptStringOrConceptCodeError(msg)

        if concept_string_or_code.count(".") == 1:
            domain, concept_code = concept_string_or_code.split(".")
            DomainBlueprint.validate_domain_code(code=domain)
            cls.validate_concept_code(concept_code=concept_code)
        else:
            cls.validate_concept_code(concept_code=concept_string_or_code)

    @staticmethod
    def validate_concept_string(concept_string: str) -> None:
        """Validate that a concept code follows PascalCase convention."""
        if "." not in concept_string or concept_string.count(".") > 1:
            msg = (
                f"Concept string '{concept_string}' is invalid. It should contain a domain in snake_case "
                "and a concept code in PascalCase separated by one dot."
            )
            raise ConceptStringError(msg)
        domain, concept_code = concept_string.split(".", 1)

        DomainBlueprint.validate_domain_code(domain)
        if not is_pascal_case(concept_code):
            msg = f"Concept code '{concept_code}' must be PascalCase (letters and numbers only, starting with uppercase, without `.`)"
            raise ConceptCodeError(msg)

        # Validate that if the concept code is among the native concepts, the domain MUST be native.
        if not SpecialDomain.is_native(domain=domain) and concept_code in NativeConceptEnum.values_list():
            msg = (
                f"Concept string '{concept_string}' is invalid. "
                f"Concept code '{concept_code}' is a native concept, so the domain must be '{SpecialDomain.NATIVE}', "
                f"or nothing, but not '{domain}'"
            )
            raise ConceptStringError(msg)

        # Validate that if the domain is native, the concept code is a native concept
        if SpecialDomain.is_native(domain=domain):
            if concept_code not in NativeConceptEnum.values_list():
                msg = (
                    f"Concept string '{concept_string}' is invalid. "
                    f"Concept code '{concept_code}' is not a native concept, so the domain must not be '{SpecialDomain.NATIVE}'."
                )
                raise ConceptStringError(msg)

    @field_validator("refines", mode="before")
    @classmethod
    def validate_refines(cls, refines: str | None = None) -> str | None:
        if refines is not None:
            if not NativeConceptManager.is_native_concept(refines):
                msg = f"Forbidden to refine a non-native concept: '{refines}'. Refining non-native concepts will come soon."
                raise ConceptBlueprintError(msg)
            cls.validate_concept_string_or_code(concept_string_or_code=refines)
        return refines

    @model_validator(mode="before")
    @classmethod
    def model_validate_spec(cls, values: dict[str, Any]) -> dict[str, Any]:
        if values.get("refines") and values.get("structure"):
            msg = (
                f"Forbidden to have refines and structure at the same time: `{values.get('refines')}` "
                f"and `{values.get('structure')}` for concept that has the definition `{values.get('definition')}`",
            )
            raise ConceptSpecError(msg)
        return values

    def to_blueprint(self) -> ConceptBlueprint:
        """Convert this ConceptBlueprint to the original core ConceptBlueprint."""
        # TODO: Clarify concept structure blueprint
        converted_structure: str | dict[str, str | ConceptStructureBlueprint] | None = None
        if self.structure:
            converted_structure = {}
            if isinstance(self.structure, str):
                converted_structure = self.structure
            else:
                for field_name, field_spec in cast("dict[str, ConceptStructureSpec]", self.structure).items():
                    converted_structure[field_name] = field_spec.to_blueprint()

        return ConceptBlueprint(definition=self.definition, structure=converted_structure, refines=self.refines)


async def create_concept_spec(working_memory: WorkingMemory) -> ConceptSpec:
    concept_spec_draft = working_memory.get_stuff_as(name="concept_spec_draft", content_type=ConceptSpecDraft)
    concept_spec_structures_stuff = working_memory.get_stuff_as_list(name="concept_spec_structures", item_type=ConceptStructureSpec)

    structure_dict: dict[str, str | ConceptStructureSpec] = {}
    for structure_item in concept_spec_structures_stuff.items:
        structure_spec = ConceptStructureSpec(
            the_field_name=structure_item.the_field_name,
            definition=structure_item.definition,
            type=structure_item.type,
            required=structure_item.required,
            default_value=structure_item.default_value,
        )
        structure_dict[structure_item.the_field_name] = structure_spec

    return ConceptSpec(
        the_concept_code=concept_spec_draft.the_concept_code,
        definition=concept_spec_draft.definition,
        structure=structure_dict,
        refines=concept_spec_draft.refines,
    )
