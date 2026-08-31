"""Demo: the two jobs a model does, generation and embeddings.

Generation turns text into new text (the answer). An embedding turns text into a
vector of numbers that captures its meaning, so similar texts sit close together.
The assistant needs both: generation to answer, embeddings to find the right doc.

Run:  poetry run python embed_vs_generate.py "how do I return an item?"
"""

from __future__ import annotations

import sys

from mocklib import cosine, embed, generate


def main() -> None:
    """Contrast generation and embeddings on the input and compare topic similarity."""
    text = sys.argv[1] if len(sys.argv) > 1 else "how do I return an item?"

    print(f'input: "{text}"\n')
    print("GENERATION (text in, text out):")
    print(f"    {generate(text)}\n")

    print("EMBEDDING (text in, a meaning vector out):")
    print(f"    {embed(text)}\n")

    print("Embeddings let you search by meaning. Compare a few questions:")
    a = "how do I return this"
    b = "what is your return policy"
    c = "where is my order"
    va, vb, vc = embed(a), embed(b), embed(c)
    print(f'    "{a}"  vs  "{b}"   similarity {cosine(va, vb)}  (close, same topic)')
    print(f'    "{a}"  vs  "{c}"   similarity {cosine(va, vc)}  (farther, different topic)')


if __name__ == "__main__":
    main()
