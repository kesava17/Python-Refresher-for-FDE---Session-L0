"""Tests for the model layer: the interface, the mock, and the factory."""

from __future__ import annotations

from model_layer.model import MockModel, make_model


def test_default_is_offline_mock() -> None:
    """The default factory choice is the offline medium mock."""
    model = make_model()  # no env, no name
    assert model.name == "mock-medium"


def test_generate_is_deterministic() -> None:
    """The same prompt returns the same answer every time."""
    model = make_model("mock-large")
    a = model.generate("Where is my order SE-100234?")
    b = model.generate("Where is my order SE-100234?")
    assert a == b


def test_capable_model_escalates_warranty_and_out_of_scope() -> None:
    """A capable model routes warranty and out-of-scope questions to a human."""
    large = make_model("mock-large")
    assert "agent" in large.generate("Is my product under warranty?").lower()
    assert "agent" in large.generate("Do you sell laptops in the Chennai store?").lower()


def test_weak_model_over_answers_the_sensitive_cases() -> None:
    """A weak model wrongly answers a sensitive warranty question instead of escalating."""
    small = make_model("mock-small")
    # the weak model wrongly answers a warranty question instead of escalating
    assert "agent" not in small.generate("Is my product under warranty?").lower()


def test_order_and_return_are_answered_at_every_capability() -> None:
    """Every capability level answers ordinary order and return questions."""
    for name in ("mock-small", "mock-medium", "mock-large"):
        model = make_model(name)
        assert "order" in model.generate("How do I track my order?").lower()
        assert "return" in model.generate("How do I return an item?").lower()


def test_embed_shape_and_similarity() -> None:
    """Embeddings have the expected width and place same-topic texts closer together."""
    model = MockModel()
    vecs = model.embed(["how do I return this", "what is your return policy", "where is my order"])
    assert all(len(v) == 32 for v in vecs)

    def cos(a: list[float], b: list[float]) -> float:
        """Return the dot product of two vectors as a similarity score."""
        return sum(x * y for x, y in zip(a, b))

    same_topic = cos(vecs[0], vecs[1])
    diff_topic = cos(vecs[0], vecs[2])
    assert same_topic >= diff_topic


def test_unknown_model_is_a_clear_error() -> None:
    """An unknown model name raises a ValueError that names the problem."""
    try:
        make_model("gpt-does-not-exist")
    except ValueError as exc:
        assert "Unknown model" in str(exc)
    else:
        raise AssertionError("expected a ValueError for an unknown model")
