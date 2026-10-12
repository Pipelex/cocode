from pipelex.interpreter_hub import get_pipes
from pipelex.kernel.llm_ops import resolve_llm_setting_for_object, resolve_llm_setting_for_text, served_llm_model
from pipelex.pipe_operators.llm.pipe_llm import PipeLLM


class TestModelReferences:
    def test_every_llm_step_resolves_to_a_served_model(self) -> None:
        """Every LLM step of the loaded library resolves, through the model deck, to a model an enabled backend serves.

        A dry run calls no model and never follows a step's model reference to the end, so an alias pointing at a model no
        enabled backend serves passes it, and fails the first real run. This follows each reference, for text and for objects,
        as a run does, and calls no model either.
        """
        llm_pipes = [pipe for pipe in get_pipes() if isinstance(pipe, PipeLLM)]
        assert llm_pipes

        unserved_references: list[str] = []
        for llm_pipe in llm_pipes:
            choice_for_text = llm_pipe.llm_choices.for_text if llm_pipe.llm_choices else None
            choice_for_object = llm_pipe.llm_choices.for_object if llm_pipe.llm_choices else None
            setting_for_text = resolve_llm_setting_for_text(llm_choice=choice_for_text)
            setting_for_object = resolve_llm_setting_for_object(llm_choice=choice_for_object, llm_choice_for_text=choice_for_text)
            for llm_setting in (setting_for_text, setting_for_object):
                if served_llm_model(model_handle=llm_setting.model) is None:
                    unserved_references.append(f"{llm_pipe.code}: {llm_setting.model}")

        assert not unserved_references, f"LLM steps whose model no enabled backend serves: {unserved_references}"
