# Day 3 demos: run the ideas, do not just read them

Each script is a tiny, self-contained demonstration of one idea from the Day 3 lesson. This
folder is its own small Poetry project, so you run the demos the same way as everything else in
this course. Set it up once, then run any demo:

```bash
poetry install                           # once, from this demos/ folder
poetry run python demo_class_vs_function.py
```

The scripts use only the standard library, so a plain `python demo_class_vs_function.py` works
too if you prefer.

| Demo | Lesson topic | What you should see |
| --- | --- | --- |
| `demo_class_vs_function.py` | 1.1 class versus function | a one-method class and a function give the same answer; a class is the right choice for shared state |
| `demo_dataclass.py` | 1.2 dataclasses for data | a dataclass matches a hand-written class with far less code; a frozen one cannot be changed |
| `demo_dict_vs_dataclass.py` | 1.3 dict versus dataclass | a dict typo is a runtime KeyError or silent junk; a dataclass has one explicit shape |
| `demo_composition.py` | 2.1 composition over inheritance | swapping the formatter changes the output with no change to Report |
| `demo_protocol.py` | 2.2 protocols | two unrelated classes satisfy one Protocol by shape; a function accepts either |
| `demo_dependency_injection.py` | 2.3 dependency injection | the service that receives its source can be run with a real or a fake source |
| `demo_decorator.py` | 3.1 decorators | a traced() decorator prints around a call without changing the function |

The exact numbers do not matter; the pattern is the point. The lesson points you to each of these
with a "Try it" note at the matching topic.
