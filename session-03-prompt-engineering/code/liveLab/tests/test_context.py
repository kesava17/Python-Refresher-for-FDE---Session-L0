"""Tests for context engineering: retrieval, the token budget, and assembly."""

from __future__ import annotations

from model_layer.corpus import load_corpus
from prompt_layer.context import build_context, estimate_tokens, load_system_prompt, retrieve


def test_estimate_tokens_is_positive() -> None:
    """Token estimates are at least one and grow with length."""
    assert estimate_tokens("hello world") >= 2


def test_system_v2_states_the_escalation_rule() -> None:
    """The strict system prompt names its scope and its escalation rule."""
    text = load_system_prompt("v2").lower()
    assert "escalate" in text and "warranty" in text


def test_retrieve_returns_relevant_passages() -> None:
    """Retrieval surfaces a return passage for a return question."""
    docs = retrieve("How do I return an item?", load_corpus())
    assert docs and any(d["topic"] == "return" for d in docs)


def test_build_context_trims_to_a_tight_budget() -> None:
    """A tighter budget assembles no more context than a generous one."""
    passages = retrieve("How do I return an item?", load_corpus(), k=5)
    _, generous = build_context("q?", passages, "SYSTEM", budget=500)
    _, tight = build_context("q?", passages, "SYSTEM", budget=45)
    assert len(tight) <= len(generous)


def test_build_context_includes_the_question_and_json_instruction() -> None:
    """The assembled prompt ends with the question and asks for JSON."""
    prompt_text, _ = build_context("where is my order?", [], load_system_prompt("v2"))
    assert "where is my order?" in prompt_text and "JSON" in prompt_text
