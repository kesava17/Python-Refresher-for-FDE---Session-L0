# Day 2 demos: run the ideas, do not just read them

Each script is a tiny, self-contained demonstration of one idea from the Day 2 lesson. This
folder is its own small Poetry project, so you run the demos the same way you run everything
else in this course. Set it up once, then run any demo:

```bash
poetry install                       # once, from this demos/ folder
poetry run python demo_gil_cpu.py
```

The scripts use only the standard library, so a plain `python demo_gil_cpu.py` works too if you
prefer.

| Demo | Lesson topic | What you should see |
| --- | --- | --- |
| `demo_gil_cpu.py` | 1.2 the GIL, 2.2 processes | threads about the same as serial; processes faster |
| `demo_io_threads.py` | 2.1 threads for waiting | concurrent finishes far sooner than serial |
| `demo_thread_race.py` | 2.1 the catch (races) | the unsafe count comes up short; the locked one is exact |
| `demo_async.py` | 2.3 asyncio | gathered concurrently is far faster than awaited one by one |
| `demo_async_blocking_trap.py` | 2.3 the trap | the blocking version is far slower: it froze the loop |
| `demo_timeout_retry.py` | 2.5 safety | it times out and gives up in about 1s, it does not hang for 3s |
| `demo_memory_stream.py` | 3.1 generators | the eager list peak is large; the generator peak is near zero |
| `demo_generator_expr.py` | 3.1 generators | the generator is tiny and single-use (second pass is 0) |
| `demo_context_manager.py` | 3.2 context managers | "closed" prints even when the block raises |

Times and sizes vary with your machine and core count; the pattern is the point, not the exact
number. The lesson points you to each of these with a "Try it" note at the matching topic.
