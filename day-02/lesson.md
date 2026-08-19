# Day 2 · Performant and Scalable

> An enterprise-class application is judged on seven qualities: performant, scalable, reliable,
> maintainable, interoperable, trustworthy, and secure. Day 1 lays the foundation they rest on,
> and Days 2 to 7 build them one at a time.
>
> **This chapter builds two of them: performant and scalable.** Day 1 set up the tools and the
> project; today the main idea is that how fast and how far a program can go is mostly decided
> by how you write it, not by tuning it afterward.

This is the chapter for Day 2. You can read it on its own. The topic is simple to state: when a
program has a small amount of work to do, almost any code works. When it has a large amount of
work, the way the code is organized decides whether it stays quick and steady or slows to a
crawl and eventually crashes. Our goal is to understand why that happens and what to do about
it.

Think about what a typical program actually spends its time on. Some of the time it is
**waiting**: waiting for a file to be read from disk, for a database to answer, for another
service on the network to reply. Some of the time it is **working**: doing calculations, parsing
text, transforming numbers. These two kinds of time behave very differently when the workload
grows, and almost everything in this chapter comes back to telling them apart.

We will move through the material in three steps, and each step answers a question that the
previous one raises:

1. **What kind of work is this?** Is the program mostly waiting, or mostly computing? This is
   Level 1, and the answer decides everything that follows.
2. **Which tool speeds up that kind of work?** Once we know whether the work waits or computes,
   we pick the right way to do more of it at once. This is Level 2.
3. **How do we keep memory and resources under control while we do it?** Speed is not the only
   way a program fails under load; it can also run out of memory or leave files open. This is
   Level 3.

After the three steps we put them together on the `reviews-insight` service from Day 1 and
measure the result, so the improvement is a number you can see, not a claim.

As you read, look for two recurring notes. The **enterprise lens** explains why an idea matters
once real users and real data are involved. The **common trap** shows a mistake that is easy to
make and easy to miss, so you can catch it in your own code and when you review someone else's.

This chapter also comes with a set of small, runnable demos in the Day 2 workspace's `demos/`
folder. Wherever you reach a **Try it** note, stop and run the named script, and watch the idea
happen for yourself. The `demos/` folder is its own small Poetry project, so you run the demos the
same way as everything else in this course: from that folder, run `poetry install` once, then each
**Try it** is `poetry run python <name>.py`. (They use only the standard library, so a plain
`python <name>.py` works too.) The exact numbers depend on your machine and its number of cores;
the pattern is the point, not the precise figure.

## Objective

After this chapter you can:

- Look at a piece of work and say whether it is IO-bound (waiting) or CPU-bound (computing), and
  explain why that matters.
- Explain, in plain terms, what the GIL is and how it changes the way threads behave.
- Choose sensibly between threads, processes, and `asyncio` for a given task.
- Fan out many waiting calls at once, safely, with timeouts, retries, and limits.
- Process very large data without running out of memory, using generators.
- Make sure files and connections are always closed, using context managers.
- Recognize the performance and resource mistakes that pass a quick test but fail under load.

## Coverage

Day 2 has three levels, and they build on each other in order:

1. **Classify the workload.** The difference between waiting and computing, and the one fact
   about Python (the GIL) that makes the difference matter.
2. **Choose the model.** The three tools for doing more at once (threads, processes, and
   `asyncio`), when each fits, and how to use them safely.
3. **Stream and release.** Generators, so memory stays flat on huge data, and context managers,
   so resources are always cleaned up.

At the end there is a recap, a pointer to the live lab, and two offline assignments.

---

## Level 1: Classify the workload

Everything in this chapter starts with a single question about the work in front of you: **is
the program mostly waiting, or mostly computing?** It sounds almost too simple to matter, but the
answer decides which tools will help and which will do nothing. So before we reach for any tool,
we learn to answer it. That is all Level 1 is: learning to classify the work, and understanding
the one rule of Python that makes the classification so important.

### 1.1 Two kinds of work: waiting and computing

Here is a familiar picture. Imagine you are cooking a large meal. Some tasks are **active work**:
chopping vegetables, stirring a sauce. Your hands are busy the whole time. Other tasks are
**waiting**: the water has to come to a boil, the bread has to bake. During those, your hands are
free; you are just waiting for something else to finish.

Programs are the same, and we give the two kinds names.

**IO-bound work spends most of its time waiting** for something outside the processor. "IO"
stands for input and output: reading a file, querying a database, calling another service over
the network. While the program waits for the reply, the processor sits idle. In most business
applications, a large share of the work is this kind: talking to databases, reading files, and
calling other services.

**CPU-bound work spends most of its time computing.** "CPU" is the processor. This is work like
doing arithmetic on large amounts of data, parsing text, compressing a file, or hashing. The
processor is busy the entire time; there is no waiting to fill.

Why do we care about this distinction so much? Because the two kinds of work are made faster by
completely different means, and using the wrong means gives you nothing:

- To speed up **IO-bound** work, you **overlap the waiting**. While one file is being read, you
  can start reading another. While you wait for one service to reply, you can send more requests.
  Because waiting is cheap (the processor is idle anyway), a single machine can have thousands of
  these waits happening at the same time.
- To speed up **CPU-bound** work, overlapping does not help, because there is no idle time to
  fill; the processor is already busy. The only way to go faster is to **do the computing on more
  processors (cores) at once**, or to hand the heavy calculation to faster, lower-level code.

If you are not sure which kind you have, here is a quick test. Imagine you upgraded the network
to be twice as fast but left the processor the same. Would the task finish sooner? If yes, it was
waiting on the network, so it is IO-bound. If the task would only finish sooner with a faster
processor, it is CPU-bound.

**The common trap.** When something is slow, the reflex is often to "make it parallel" by adding
a pool of threads, without first asking which kind of work it is. As we are about to see, for
computing-heavy work that does nothing, and can even make it slightly slower. The first question
is never "how do I parallelize this," it is "is this waiting or computing."

That trap points straight at the reason the classification matters so much in Python
specifically. To understand why threads help one kind of work and not the other, we need to meet
one rule that is unique to how Python runs.

### 1.2 Why Python treats the two differently: the GIL

You may have heard that "Python threads don't really run in parallel." That statement is half
true, and the reason is a single design decision in the standard Python interpreter (called
CPython) named the **Global Interpreter Lock**, or **GIL**.

Here is the GIL in one sentence: **only one thread can run Python code at a time.** A thread is
just a separate line of execution inside your program; you can have several, but the GIL is like
a single "permission to run Python" token, and only the thread holding the token may run Python
instructions at any given instant.

Now watch how that one rule interacts with the two kinds of work from Section 1.1. This is the
whole point of the GIL, so read it slowly.

- **For IO-bound (waiting) work, threads still help.** When a thread makes a call that waits, for
  the network or the disk, it does not need to run Python code during the wait, so it **hands the
  token back** while it waits. Another thread picks up the token and runs. So even though only
  one thread runs Python at any instant, many threads that are mostly waiting can overlap their
  waits nicely. This is exactly the "overlap the waiting" idea, and it works.
- **For CPU-bound (computing) work, threads do not help.** If every thread wants to run Python
  code all the time, they cannot, because there is only one token. They take turns, one at a
  time, and you get no speedup at all. In fact you can get a small slowdown, because the program
  spends a little effort passing the token back and forth.

Go back to the kitchen for a moment. Think of the GIL as there being only one cutting board.
Chopping (running Python code) can only be done by one cook at a time. But when a cook is just
waiting for water to boil, they step away from the board so another cook can chop. More cooks
speed things up only if they spend a lot of time waiting; if they all need the one board the
whole time, extra cooks just queue.

So if threads cannot speed up computing-heavy work, what can? Two answers, and we will use both
later in the chapter:

- Use **separate processes** instead of threads. A process is a whole separate copy of the
  program, and crucially each one has **its own token**. Eight processes can genuinely run on
  eight cores at the same time.
- Or hand the heavy calculation to **lower-level code** that steps outside Python. Libraries
  written in C, such as the numerical library NumPy, release the token while their fast internal
  code runs, so they can use the machine fully even from one Python thread.

> A note for later: recent versions of Python have started to offer an experimental mode without
> the GIL, and the situation is slowly changing from release to release. For now, and for almost
> all code you will read and write today, the GIL is in force, so this is the correct way to
> reason about it. Treat GIL-free Python as something to confirm for a specific setup, not to
> assume.

**Enterprise lens.** The costly version of not knowing this: a team notices a computing-heavy job
is slow, adds a pool of threads, sees no improvement, and concludes "Python is just slow." The
real fix was processes or a native library. Knowing the rule up front means you reach for the
right tool the first time, instead of rebuilding after the wrong one fails.

> **Try it.** Run `poetry run python demo_gil_cpu.py`. It runs the same computing-heavy work three ways.
> You will see the thread version finish in about the same time as serial, while the process
> version is much faster (something like `serial 0.9s, threads 0.9s, processes 0.3s`). That is the
> GIL on one screen: threads cannot speed up CPU-bound work, but separate processes can.

### 1.3 This is a design choice, not a later fix

Before we move on, notice one thing about everything in Level 1. Whether work is waiting or
computing, whether it can be split across cores, whether it reads data a little at a time or all
at once, all of that is decided by **how you structure the code in the first place**. You cannot
sprinkle it on afterward. If a program loads a huge file into memory on its first line, no amount
of tuning later will undo that; the shape of the code already committed you.

This is exactly why performance and scale are Day 2, sitting right next to how you write the
code, rather than an "optimization" topic saved for the end. You are not learning to fix slow
code after the fact; you are learning to write code that was built to cope from the start.

We can now answer the first question, "what kind of work is this?" That answer points us at a
tool. Level 2 introduces the tools themselves.

---

## Level 2: Choose the model

In Level 1 we learned to ask one question, "is this waiting or computing," and we saw why the
answer matters: because of the GIL, waiting work and computing work are sped up in different
ways. Level 2 is where we meet the actual tools that do the speeding up. There are three of them,
and it will help to keep the map in mind as we go:

- **Threads**, for work that waits (IO-bound), when there is a moderate amount of it.
- **Processes**, for work that computes (CPU-bound), so we can use many cores.
- **`asyncio`**, also for work that waits, but built for very large numbers of waits at once.

We will take them in that order, because it mirrors Level 1: start with the tool for waiting
work, then the tool for computing work, then the specialized tool for waiting at huge scale.
After the three tools, we add the one thing that turns "fast" into "fast and safe."

### 2.1 Threads: for work that waits

We start with threads, because they are the natural fit for the most common case: you have many
IO-bound calls to make, and you want to overlap their waiting. Python's clean, modern way to use
threads is a **thread pool**, provided by `concurrent.futures.ThreadPoolExecutor`. A pool
manages a fixed number of worker threads for you, so you never handle raw threads by hand.

```python
from concurrent.futures import ThreadPoolExecutor


def fetch(url: str) -> str:
    ...  # a call that waits for the network, then returns a result


urls = [...]  # many URLs to fetch

# Serial: one at a time. Each call must finish before the next begins.
results = [fetch(url) for url in urls]

# Concurrent: the waits overlap, so the whole batch finishes much sooner.
with ThreadPoolExecutor(max_workers=16) as pool:
    results = list(pool.map(fetch, urls))
```

Two details in that small example are worth pausing on. The `with` block ensures the pool is
shut down cleanly once the batch is done. And `max_workers=16` sets how many calls may be in
flight at the same time; we will rely on that number again in Section 2.5 to avoid overwhelming
the service we are calling.

There is one danger that comes with threads, and it comes from their biggest advantage. Threads
all share the same memory, which is what makes them lightweight. But it also means two threads
can touch the same variable at the same time and interfere with each other:

```python
count = 0

def worker() -> None:
    global count
    count += 1  # not as simple as it looks: read count, add 1, write it back
```

That single line `count += 1` is really three steps: read the current value, add one, and write
it back. If two threads do those steps at overlapping moments, they can both read the same
starting value and both write back the same result, so one of the increments is lost. Bugs like
this are hard to find because they only appear sometimes, under the right timing.

The way to avoid the whole problem is to **not share changing data between threads**. Instead,
have each task return its result, and combine the results after all the threads are done, which
is exactly what `pool.map` above does. When you truly must share, use a lock or a thread-safe
structure such as `queue.Queue`.

**The common trap.** A thread pool whose workers all write into one shared list or dictionary.
It passes a small test, then loses or corrupts data once real traffic makes the timing overlap.
When reviewing threaded code, look for any changing value that more than one worker touches.

> **Try it.** Run `poetry run python demo_io_threads.py`: twenty waits that take about 2 seconds one
> after another finish in about 0.1 seconds through a thread pool, because the waits overlap. Then
> run `poetry run python demo_thread_race.py` to see the danger from this section: eight threads adding
> to one shared counter without a lock lose thousands of updates (the `unsafe` total lands far
> below the expected 40000), while the locked version comes out exactly right.

Threads handle waiting work. But Level 1 warned us that they do nothing for computing-heavy work,
because of the GIL. So what do we use for that? That is the next tool.

### 2.2 Processes: for work that computes

When the work is CPU-bound, we need real parallelism, and Section 1.2 already told us how to get
it: separate processes, each with its own GIL. The nice part is that the tool looks almost
identical to the thread pool, so moving from one to the other is a small change:

```python
from concurrent.futures import ProcessPoolExecutor


def transform(chunk: bytes) -> int:
    ...  # heavy computation: parsing, math, compression


with ProcessPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(transform, chunks))
```

Each worker here is a full, separate Python process, so eight of them really do run on eight
cores at once. That is the payoff. But processes are not free, and it is important to understand
the cost so you know when they are worth it. Because the workers are separate programs, they do
not share memory with each other, so any data you send to a worker, and any result it sends back,
has to be **copied across the process boundary** (Python calls this "pickling"). If the pieces of
data are huge, or the calculation on each piece is tiny, the copying can cost more than the
computing you saved.

The rule of thumb that follows: process pools pay off when **each task does a real amount of
computing on a moderate amount of data**. Big computation, modest data per task, and the copying
is a small tax on a large gain.

**The common trap.** This is the mirror image of the threads trap. Using a thread pool on
genuinely CPU-bound work gives no speedup, because of the GIL. Using a process pool on lots of
tiny tasks can be slower than doing nothing, because the copying overwhelms the work. The lesson
is the same one from Level 1: match the tool to the kind of work.

We now have a tool for waiting (threads) and a tool for computing (processes). There is one more
tool, and it exists for a specific situation the thread pool handles less well: not just many
waiting calls, but a very large number of them.

### 2.3 `asyncio`: for very many waits at once

Threads work well for overlapping waits, but each thread carries some memory and bookkeeping, so
running tens of thousands of threads becomes wasteful. `asyncio` is Python's answer for that
situation: it lets a **single thread** juggle a very large number of waiting operations, using a
coordinator called an **event loop** instead of one thread per call.

```python
import asyncio


async def fetch(url: str) -> str:
    ...  # a non-blocking call that lets others run while it waits


async def main(urls: list[str]) -> list[str]:
    return await asyncio.gather(*(fetch(url) for url in urls))
```

The new keyword is `await`. When a coroutine (a function defined with `async def`) reaches an
`await` on something that has to wait, it hands control back to the event loop, which then runs
another coroutine that is ready. When the awaited result arrives, the loop comes back to it.
Because everything runs on one thread, taking turns cooperatively, one thread can keep thousands
of calls in progress.

There is one rule you cannot break, and it follows directly from "everything runs on one thread."
**Never do slow, blocking work inside a coroutine.** If a coroutine calls something that blocks
the thread (an old-style synchronous database call, a plain `time.sleep`, or a heavy computation)
then the single thread is stuck there, and every other awaiting operation is frozen behind it. In
async code you use async-aware libraries, and when you genuinely must run blocking or CPU-heavy
work, you push it off to a thread or process pool with `asyncio.to_thread` or
`loop.run_in_executor`.

This is a specific case of a broader design rule worth stating on its own: **keep long or blocking
work off the thread that handles requests.** Whether it is an async event loop or an ordinary web
server's worker thread, a slow computation or a blocking call sitting on that thread holds up
everything waiting behind it. When the work is heavy, move it to a separate thread or process
pool and let the main thread stay responsive.

**The common trap.** This is the most frequent `asyncio` mistake: an `async def` that calls a
blocking library inside it, for example a synchronous `requests.get` or a plain `time.sleep`. The
code runs and even looks concurrent, but it is not, because that one blocking call freezes the
loop. When reviewing async code, check every `async def` for a call that is not awaited and is
not instant.

> **Try it.** Run `poetry run python demo_async.py`: fifty waits done one `await` at a time take a few
> seconds, but `asyncio.gather` runs them together in about 0.1 seconds on a single thread. Then run
> `poetry run python demo_async_blocking_trap.py` to see the rule that breaks people: swapping the
> non-blocking wait for a blocking `time.sleep` inside the coroutines makes the same work roughly
> twenty times slower, because one blocking call freezes the whole loop.

That covers the three tools. Before we make them safe, one short, practical footnote about a term
you will hear.

### 2.4 A note on affinity

**Affinity** means pinning a piece of work to a specific processor core so it keeps running on
the same core and its data stays in that core's fast local memory (its cache). It matters mainly
for long-running, computing-heavy, lower-level numeric work, where cache locality and steady
timing are worth tuning. In practice it is usually handled for you: the big numeric libraries
manage their own worker threads and affinity. So treat this as a term to recognize, not a dial to
turn: if you are hand-writing parallel numeric code and the timing is uneven, affinity and a
library's own threading settings are where to look. For ordinary application code you do not set
it by hand.

### 2.5 Making concurrency safe

So far Level 2 has been about making work faster. But speed is not the only goal, and here is
why. The moment your program calls other systems, it depends on things that can be slow, can
fail, and can limit how often you may call them. A fast fan-out that falls apart the first time a
dependency misbehaves is worse than a slow one that keeps working. So the last part of Level 2 is
the discipline that makes concurrency safe. There are four habits, and every one of them is about
what happens when something goes wrong:

- **Timeouts.** Never wait forever for a call to return. Give every external call a time limit, so
  that one stuck dependency cannot tie up a worker indefinitely.
- **Retries, with a limit and a growing delay.** Brief failures are normal, so it is fine to try
  again a few times, waiting a little longer between attempts. But always cap the number of
  attempts; retrying without end is how one slow dependency turns into a full outage.
- **Concurrency limits.** Cap how many calls run at once (this is the `max_workers` number from
  Section 2.1, or a semaphore). If you fire ten thousand requests at a service in one burst, you
  can overwhelm the very service you depend on.
- **Backpressure.** If your program produces work faster than it can process it, slow the producer
  down rather than letting unfinished work pile up in memory. A queue with a maximum size does
  this automatically.

Here is a small example that combines a timeout with a bounded retry:

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout


def fetch_with_retry(url: str, attempts: int = 3, timeout: float = 2.0) -> str:
    """Call fetch with a time limit per attempt and a fixed number of retries."""
    for attempt in range(1, attempts + 1):
        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(fetch, url)
            try:
                return future.result(timeout=timeout)
            except FuturesTimeout:
                if attempt == attempts:
                    raise  # out of attempts: fail clearly rather than hang
    raise RuntimeError("unreachable")
```

**Enterprise lens.** A service that stays responsive when a dependency slows down is the
difference between "one system is a bit slow today" and "the slowness spread and took everything
down with it." Timeouts, limits, and retries are not extras added at the end; they are part of
what makes concurrency safe to run for real.

**The common trap.** Quickly written concurrent code almost never includes a timeout or a limit,
because on a good day the dependency is fast and healthy and none of it seems necessary. When you
review such code, treat an external call with no timeout as a bug, not a matter of style.

> **Try it.** Run `poetry run python demo_timeout_retry.py`. It calls a dependency that is stuck for 3
> seconds, but with a 0.3 second timeout and three attempts it gives up cleanly in under a second
> instead of hanging. That is the difference between a service that degrades and one that freezes.

We have now made the work both faster and safer. There is one kind of failure left that none of
these tools touch, and it has nothing to do with speed. That is what Level 3 is about.

---

## Level 3: Stream and release

Levels 1 and 2 were about doing work faster. But a program can hold up perfectly on speed and
still fall over under load for a different reason: it runs out of **memory**, or it runs out of
**resources** like open files and connections. These two problems are quieter than a slowdown,
because they often appear only after the program has been running for a while or on data larger
than any test used. Level 3 is the two habits that prevent them: streaming data instead of
holding it all, and always releasing resources you open. We take memory first, then resources.

### 3.1 Generators: process data without holding it all

The single most common way a data program dies in production is that it tried to load everything
into memory at once. It worked perfectly on a sample of a thousand rows during testing, and then
fell over on the real file of fifty million rows. The fix is to **stream**: handle the data one
piece at a time and never keep the whole thing in memory.

Python's tool for this is the **generator**. A generator is a function that produces its values
one at a time using the keyword `yield`, instead of building a whole list and returning it. Each
value is produced when it is asked for and then forgotten, so the amount of memory used stays
flat no matter how large the input is. Compare the two versions:

```python
from collections.abc import Iterator


# Eager: builds the entire list in memory. Fine for 1,000 rows, fatal for 50 million.
def read_all(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f]


# Streaming: hands back one line at a time. Memory stays flat at any size.
def read_stream(path: str) -> Iterator[str]:
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield line.strip()
```

The eager version returns a list, so every line lives in memory at once. The streaming version
`yield`s a line and moves on, so only the current line is held. You might ask: if I never hold
all the data, how do I compute a total or a count over it? The answer is to accumulate as you go,
keeping only the small running result rather than the data itself:

```python
def count_and_distinct(lines: Iterator[str]) -> dict[str, int]:
    total = 0
    seen: set[str] = set()
    for line in lines:
        total += 1
        seen.add(line)
    return {"total": total, "distinct": len(seen)}
```

This keeps only a running count and a set of the distinct values, never the file itself. On a
fifty-million-row file, the eager approach might need many gigabytes of memory while this one
needs almost none. That is the difference between a program that keeps working as the data grows
and one that crashes when it gets big.

This one-at-a-time behavior has a name: **lazy evaluation**. The generator does no work until
something asks it for the next value, and it never runs ahead of what is needed. A generator is
one kind of **iterator**, which is Python's general idea of an object you can pull values from,
one at a time, with a `for` loop. There is also a streaming counterpart to the list
comprehension, called a **generator expression**: write it with parentheses instead of square
brackets, and it produces its values lazily instead of materializing a whole list.

```python
doubled = [x * 2 for x in rows]   # list comprehension: builds the entire list in memory
doubled = (x * 2 for x in rows)   # generator expression: streams one value at a time
```

One property of generators is worth remembering so it does not surprise you: a generator is
**single-use**. Once you have looped over it, it is exhausted, and looping again yields nothing.
If you need the data a second time, either open the stream again or, only when the data genuinely
fits in memory, collect it into a list once, on purpose.

**The common trap.** The neat-looking line `data = [transform(x) for x in load_everything()]`.
That single list comprehension pulls the entire dataset into memory. It reads cleanly and works
on small data, and it runs the machine out of memory on real data. When you review code, for any
list comprehension or `list(...)` built from an outside source, ask whether it truly needs all
the data at once, or whether it could stream.

> **Try it.** Run `poetry run python demo_memory_stream.py`: summing five million numbers as a list
> peaks at hundreds of megabytes, while the generator version peaks near zero, for the same answer.
> Then run `poetry run python demo_generator_expr.py` to see that a generator expression is tiny next to
> the equivalent list (a couple of hundred bytes versus hundreds of kilobytes) and is single-use:
> the second pass over it sums to 0, because it is already spent.

Generators keep memory under control. The same idea, "clean up after yourself as you go," applies
to the other scarce thing a program holds: open files and connections. That is the second habit.

### 3.2 Context managers: always clean up

Every file you open, every network socket, and every database connection is a limited resource.
The operating system allows only so many open files, and a database allows only so many
connections. If your code opens them and forgets to close them, then under load you run out, and
the program fails, often long after and far away from the code that actually leaked.

Python's tool for guaranteeing cleanup is the **context manager**, used with the `with`
statement. Its key property is that the cleanup happens **even if an error occurs** inside the
block:

```python
with open("data.csv", encoding="utf-8") as f:
    process(f)
# f is closed here, whether process() finished normally or raised an error.
```

That "even if an error occurs" is the whole value. If you instead wrote `f = open(...)` and then
`f.close()` at the end, any error in between would skip the `close()` and leak the file. The
`with` form cannot leak, because closing is guaranteed on the way out, success or failure.

You are not limited to files. You can write a context manager for anything that must be acquired
and then released, and the simplest way is the `contextlib.contextmanager` decorator:

```python
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def timer(label: str) -> Iterator[None]:
    import time

    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{label}: {time.perf_counter() - start:.3f}s")


with timer("load"):
    records = load()
```

Read that shape carefully, because you will reuse it: everything before the `yield` is setup that
runs when you enter the `with`, and everything in the `finally` after the `yield` is teardown
that runs when you leave, no matter what happened inside. For a real resource such as a database
connection, the teardown is where you close it or return it to a pool.

Three habits go with using resources well. **Open late and close promptly:** acquire a resource
just before you need it and release it as soon as you are done, so its lifetime is short and
predictable. **Never rely on the garbage collector to close things:** Python will eventually
clean up a file you abandoned, but "eventually" is not something you can depend on, and under
load the resource runs out long before the collector gets around to it, so always close
explicitly, which a `with` does for you. **Reuse expensive resources through a pool:** opening a
database connection is slow, so real systems keep a pool of already-open connections and hand
them out, using a context manager that returns each connection to the pool instead of closing it.

**The common trap.** Code that opens a file or a connection and never closes it, or closes it
only on the success path so an error leaks it. Under load these small leaks add up silently until
nothing more can be opened. When you review code, every resource that is acquired should sit
inside a `with`.

**Enterprise lens.** Streaming and guaranteed cleanup are what let the same code that passed on a
small sample keep working on the real volume of data and the real length of time it runs. A
service that leaks one connection per request looks fine in a demo and fails after a couple of
weeks in production.

> **Try it.** Run `poetry run python demo_context_manager.py`. Watch the order of the printed lines: on
> the error path, `closed` still prints before the exception is caught. That is the whole promise of
> `with`: the cleanup runs whether the block finishes normally or raises.

---

## The build: `reviews-insight`, made performant

We can now put all three levels together on the `reviews-insight` service from Day 1. Day 1 left
it reading the whole CSV into a list and printing a summary, which is fine for five rows and
wrong for fifty million. In this section we apply Level 3 (stream instead of load) and Level 2
(overlap waiting work) and then measure both, so the improvement is a number. The live lab walks
every step with commands; here is the shape.

**Step 1, apply Level 3 to memory: stream instead of loading.** Replace the eager loader from Day
1 with a streaming one that also cleans up its file, combining the generator and the context
manager from Level 3.

```python
"""Load records from a CSV file: eagerly (Day 1) or as a stream (Day 2)."""

from __future__ import annotations

import csv
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def open_records(path: str) -> Iterator[Iterator[dict[str, str]]]:
    """Open the CSV and hand back a stream of rows. Closes the file on the way out, always."""
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"data file not found: {path}")
    handle = file.open(newline="", encoding="utf-8")
    try:
        reader = csv.DictReader(handle)
        yield ({key: str(value) for key, value in row.items()} for row in reader)
    finally:
        handle.close()
```

**Step 2, summarize in constant memory.** Fold the stream into a running count and a set of
product ids, holding neither the rows nor a copy of the file, exactly as in Section 3.1.

```python
from collections.abc import Iterator


def summarize_stream(records: Iterator[dict[str, str]]) -> dict[str, int]:
    reviews = 0
    products: set[str] = set()
    for record in records:
        reviews += 1
        products.add(record["product_id"])
    return {"reviews": reviews, "products": len(products)}
```

**Step 3, prove the memory is flat.** Use Python's `tracemalloc` tool to measure the memory used
by the old eager path and the new streaming path on a large generated file. The eager peak grows
with the file; the streaming peak stays nearly flat. The measurement is the proof, not a claim.

**Step 4, apply Level 2: overlap waiting work.** Suppose each review is enriched by looking up its
product's category from an external service, one call per record. That lookup waits on the
network, so it is IO-bound, which from Level 1 and 2 means threads are the right tool. Run the
lookups first one at a time, then through a thread pool, and compare.

```python
import time
from concurrent.futures import ThreadPoolExecutor


def fetch_category(product_id: str) -> str:
    time.sleep(0.05)  # stands in for a real network call to an external service
    return "priority" if product_id.endswith(("0", "5")) else "standard"


def enrich_concurrent(product_ids: list[str], workers: int = 16) -> list[str]:
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(fetch_category, product_ids))
```

Because `fetch_category` spends its time waiting, the thread pool overlaps those waits and the
whole batch finishes in roughly the serial time divided by the number of workers. And here is the
Level 1 lesson made concrete: if this lookup were CPU-bound instead of waiting, the same thread
pool would give almost nothing, and we would reach for a process pool.

The live lab does all four steps with real commands and expected output. When you finish, the
same small service streams in constant memory and enriches concurrently, and you have two
measured numbers, a flat memory profile and a serial-versus-concurrent benchmark, that prove it.

---

## Recap

Reading the three levels back as one connected idea:

- **Level 1, classify.** First ask whether the work is waiting (IO-bound) or computing
  (CPU-bound). Because of the GIL, only one thread runs Python at a time, so threads help waiting
  work but not computing work.
- **Level 2, choose the tool.** Threads for waiting work, processes for computing work (they each
  get their own GIL), and `asyncio` for very large numbers of waits. Then make it safe with
  timeouts, bounded retries, concurrency limits, and backpressure.
- **Level 3, stream and release.** Use generators so memory stays flat on huge data, and context
  managers so files and connections are always closed, even when something fails.
- **It is a design choice.** All of this is decided when you write the code, not in a later
  tuning pass. Three habits capture it: pick the concurrency model before you write, based on the
  kind of work; keep long or blocking work off the thread that handles requests; and bound memory
  and connections from the start, by streaming data and by releasing resources with context
  managers.

The review checklist for the whole day: given a piece of code, ask which kind of work it is,
whether the concurrency tool matches that kind, whether every external call has a timeout,
whether any changing data is shared unsafely between workers, whether it holds data it could
stream, and whether every resource it opens is guaranteed to close. Those questions are what turn
"it ran once" into "it will keep working under real load."

**Next:** the [live lab](live-lab.md) makes `reviews-insight` stream and enrich concurrently,
with a memory profile and a benchmark as proof. Then two offline assignments apply the same
performance layer to IoT telemetry data and to financial transactions.
