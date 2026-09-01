"""The prompt and output layer of the Sunrise Support Deflection Assistant.

Built in Session 3 on top of Session 2's model layer. It turns a free-text model into a
component the rest of the assistant can trust: a validated ``Answer`` produced two ways
(prompt-for-JSON and function-calling), engineered context within a token budget, an
aligned system prompt, and input and output guardrails that escalate rather than guess.
"""
