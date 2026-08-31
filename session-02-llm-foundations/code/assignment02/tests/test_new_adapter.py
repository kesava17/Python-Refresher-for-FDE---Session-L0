"""Assignment 2 target. Make these pass by adding an 'echo' adapter to make_model().

An EchoModel.generate(prompt) must return "echo: " + prompt. Wire it into make_model()
so make_model("echo") (and LLM_MODEL=echo) selects it, without changing any caller. The
offline mock must remain the default. See assignment-02.md.
"""

from __future__ import annotations

from model_layer.model import make_model


def test_echo_adapter_selected_by_name() -> None:
    """The factory selects the echo adapter by name and it echoes the prompt."""
    model = make_model("echo")
    assert model.generate("hello") == "echo: hello"


def test_default_is_still_the_offline_mock() -> None:
    """The offline mock stays the default when no name is given."""
    assert make_model().name == "mock-medium"
