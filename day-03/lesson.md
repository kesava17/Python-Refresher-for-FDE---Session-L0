# Day 3 · Maintainable

> An enterprise-class application is judged on seven qualities: performant, scalable, reliable,
> maintainable, interoperable, trustworthy, and secure. Day 1 lays the foundation they rest on,
> and Days 2 to 7 build them one at a time.
>
> **This chapter builds: maintainable.** Day 1 set up the environment and Day 2 made the app fast
> and scalable; today (Day 3) we make it maintainable, so it can be read, changed, and extended.
> Reliability comes next, on Day 4.

Maintainable code is code that is easy to read and easy to change. In a real business, code is
read and changed far more often than it is written, so the design decides how long a program
survives. The hard part is not knowing the tools. It is knowing which tool to use where.

That is the idea for the whole day. A programming language gives you many **constructs**, which
are just its building tools: a class, a function, a decorator, and so on. We know all of them.
Our rule is simple: **do not use a construct just because you know it.** Each one has a place
where it helps and a place where it only adds weight. Before you reach for a construct, ask one
question: does it make this piece of code easier to read and change?

We work in three parts. First, the main styles of programming (paradigms) and the constructs each
one gives you, in plain terms. Second, how Python writes those same constructs, in the same order.
Third, the practical rule for each one, when to use it and when not to, using SOLID and a few
design patterns as a guide. Running through all three parts is one small example, a **reviews
service** that reads product reviews and reports a summary. At every step we ask the same
question of the example: did this construct make it better or worse to read and change?

Alongside this chapter is a `demos/` folder of short, runnable scripts, one per idea. Wherever you
reach a **Try it** note, stop and run the named script. From that folder, run `poetry install`
once, then each **Try it** is `poetry run python <name>.py`.

## Objective

After this chapter you can:

- Name the main paradigms (dynamic, object-oriented, functional, metaprogramming) and the
  constructs each one gives you.
- Write those constructs in Python: type hints, classes and dataclasses, composition and
  protocols, functions, and decorators.
- Decide when to use each construct and when to leave it out, using a simple when and when-not
  check.
- Apply SOLID and a few design patterns as guidance, not as a checklist.
- Take a rough service and make it simpler to read and change, one construct at a time.

## Coverage

Day 3 has three parts:

1. **Paradigms and their constructs**, in general: dynamic, object-oriented, functional, and
   metaprogramming, and how each helps or hurts readability and maintainability.
2. **The same constructs in Python**, in the same order, where we start building the reviews
   example.
3. **Best practices**: when to use each construct and when not to, with SOLID and design patterns,
   applied to the reviews example from a rough first version to a clean one.

At the end there is a recap, a pointer to the live lab, and two offline assignments.

---

## Part 1: Paradigms and their constructs

Before the details, two plain definitions.

A **construct** is a building tool the language gives you: a variable, a function, a loop, a class,
a decorator. You already use constructs every day.

A **paradigm** is a *style* of putting those constructs together to organize a whole program. It is
a way of thinking about code. The same task can be written in different paradigms, the way the same
house can be built in brick or in wood. No paradigm is the one correct answer. Most real programs
mix several, and Python lets you use them all together.

Why does this matter for maintainable code? Because each paradigm gives you tools that make some
kinds of code much easier to read and change, and other kinds harder. If you know only one style,
you force every problem into it. If you know all of them, you can pick the one that fits and keep
the code simple.

The style most people start with is **procedural** (also called imperative): you write statements
one after another, group them into functions, and the program runs top to bottom, step by step,
like a recipe. It is good for straight-line logic, and it is the baseline the rest build on. The
four paradigms below are not replacements for it; they are extra tools you reach for when plain
procedural code starts to get hard to manage. We look at dynamic, object-oriented, functional, and
metaprogramming.

### 1.1 Dynamic

**What "dynamic" means.** In some languages you must declare the type of every variable before you
use it, such as `int count = 0`, and a compiler checks those types before the program ever runs.
That is called **static** typing. A **dynamic** language works the other way: you do not declare
types, the type belongs to the value, and it is checked while the program runs. A picture that
helps: static typing is like labelled boxes that each accept only one kind of item; dynamic typing
is like a box that holds anything, and you see what is inside when you open it.

The dynamic style has two main constructs.

**Dynamic binding.** A name (a variable) is just a label you can stick on any value, and later move
to a value of a different type.

```python
x = 42        # x labels a number
x = "hello"   # the same name now labels text: allowed, because the type is on the value
```

This is why you write less setup code, and it lets you write general code that does not care about
exact types.

**Duck typing.** This is the more important idea, so here it is in full. The name comes from the
saying, "If it walks like a duck and quacks like a duck, then it is a duck." In code it means: you
do not ask "what type is this object?" You just call the method you need, and any object that has
that method works, whatever class it came from.

Here is an example. Say you have a function that prints a report from a data source:

```python
def print_report(source):
    text = source.read()     # we only need something that has a read() method
    print(text)
```

Many different objects can be passed to `print_report`: a file, a network response, an in-memory
text buffer, or a small fake object you write for a test. None of them share a common parent class.
They just each happen to have a `read()` method, and that is all `print_report` cares about.

Now compare this with a static language. There, to pass an object into `print_report`, the object
usually has to be declared as a specific type, or made to implement a named interface, and the
compiler checks that before the program runs. Duck typing removes that requirement up front: Python
does not check anything when you define the function. It checks, at the exact moment `source.read()`
runs, whether `source` really has a `read` method. If it does, the call runs; if it does not, you
get an `AttributeError` on that line.

**Why duck typing helps maintainability.** Your code depends on *behaviour* (it has a `read()`
method), not on a specific class. So you can add a brand new kind of source later without touching
`print_report`, and you can test it by passing a tiny fake object instead of a real file or a real
network call. This is a large part of what makes Python code easy to extend and easy to test.

**The risk, and the fix.** Because the check happens only when the line runs, passing the wrong
object is not caught until then, and if that path is rare the error can appear late. The fix is to
add **type hints** (short notes that say what is expected) and run a checker such as mypy that reads
them before the code runs. You can even say "this must be anything that has a `read()` method",
using a Protocol (Part 2), so you keep the flexibility and still catch a wrong object early.

**SOLID link.** Duck typing is the everyday form of the **D** in SOLID, Dependency Inversion:
depend on what an object can *do* (its methods), not on its exact class.

### 1.2 Object-oriented

**What object-oriented means.** This style bundles **data** together with the **behaviour** (the
functions) that work on that data, into one unit called an **object**. Instead of keeping data in
one place and the functions that use it somewhere else, they live together. A real-world picture: a
car has data (speed, fuel level) and things it can do (accelerate, brake). An object in code is the
same idea, data plus the actions that belong with it.

**Class and object.** A **class** is a blueprint, the design. An **object** (also called an
instance) is one real thing built from that blueprint. You write the class once and make many
objects from it: one `Car` class, thousands of car objects, each with its own speed and fuel.
**Encapsulation** means the object keeps its data inside and controls how it changes, so the rest
of the program cannot reach in and put it in a bad state. For example, a bank account object might
allow only `deposit` and `withdraw`, so the balance can never be set to a random value from
outside.

Two objects can be connected in two very different ways, and choosing between them is one of the
most important design decisions you make: **inheritance** and **composition**.

**Inheritance (an "is-a" link).** One class can build on another and get its data and methods for
free, then add or change some. We say the new class **inherits** from the old one, and the link is
"is-a": a `SavingsAccount` **is a** `BankAccount`, so it inherits from `BankAccount` and adds
interest on top.

```python
class BankAccount: ...
class SavingsAccount(BankAccount): ...   # SavingsAccount IS A BankAccount
```

Inheritance is useful when there is a true, stable "is-a" relationship. But it has a serious
downside when it is overused. A deep chain (A is a B is a C is a D) becomes rigid: a change to the
class at the top silently affects everything below it, and to understand one object you have to read
up and down the whole chain. This is a common reason code becomes hard to change.

**Composition (a "has-a" link).** Instead of inheriting, an object **holds** another object and uses
it. The link is "has-a": a `Car` **has an** `Engine`. The car keeps an engine object and calls its
methods, and you can swap that engine for a different one without changing the car.

```python
class Car:
    def __init__(self, engine):
        self.engine = engine        # a Car HAS AN Engine (composition)

    def start(self):
        self.engine.turn_on()
```

**Which to use: prefer composition.** The guideline, one of the best known in design, is **prefer
composition over inheritance**. Use inheritance only for a true, stable "is-a" (or to define an
interface, covered later). Use composition for almost everything else, especially when your real
goal is just to reuse some behaviour. Composition keeps the parts small and independent, so you can
change or swap one without disturbing the others, while deep inheritance ties them together. A quick
test: if you are about to inherit only to reuse a method, that is a sign to use composition instead.
Say "has-a", not "is-a", unless the "is-a" is genuinely true.

**Polymorphism.** The word means "many shapes". Different objects offer the **same method name**, so
one piece of code works with all of them without knowing which exact one it holds. For example,
`Circle`, `Square`, and `Triangle` each have an `area()` method; a function that adds up areas works
on any shape, and you can add a new shape later with no change to that function.

**How it helps readability and maintainability.** When a thing has both data and behaviour, or holds
state that several steps share, a class keeps them in one place, gives them a name, and hides the
messy details behind a small set of methods. A new reader can understand one object without reading
the whole program.

**The risk.** Object-oriented code is easy to overuse. Making a class for something that is really
just a function, or building deep inheritance trees, adds weight and makes code harder to follow,
not easier.

**SOLID.** Object-oriented code is where the SOLID principles live. They are five habits, one per
letter, in plain terms:

- **S, Single Responsibility.** Each class or function should do one job, so it has one reason to
  change.
- **O, Open-Closed.** You should be able to add new behaviour by adding new code, not by editing
  code that already works.
- **L, Liskov Substitution.** If `B` inherits from `A`, then a `B` must work anywhere an `A` is
  expected, with no surprises.
- **I, Interface Segregation.** Keep interfaces small and focused; do not force a class to depend on
  methods it does not use.
- **D, Dependency Inversion.** Depend on a small interface (a promise of what methods exist), not on
  a specific concrete class.

The headline that ties them together: prefer composition over deep inheritance, and depend on small
interfaces.

### 1.3 Functional

**What functional means.** This style builds a program mostly out of **functions** that take input
and return output, and it avoids changing shared data. The idea comes from mathematics, where a
function always gives the same answer for the same input. It has three constructs worth knowing.

**Pure functions.** A function is **pure** when two things are true: (1) the same input always gives
the same output, and (2) it changes nothing outside itself (it does not write to a global, print,
call a database, or edit its own inputs). For example, `add(2, 3)` always returns `5` and touches
nothing else, so it is pure. A function that reads the current time, or writes to a file, is **not**
pure, because its result or its effect changes from call to call.

```python
def add(a, b):          # pure: same inputs give the same output, no side effects
    return a + b

def append_now(log):    # not pure: it changes the list passed in from outside
    log.append(current_time())
```

Why it helps: a pure function is the easiest kind of code to understand and to test, because you
only look at its inputs and its output. There is nothing hidden.

**Immutability.** Data is **immutable** when it cannot be changed after it is created. If you want a
different value, you make a new one. Numbers and text in Python are already immutable; a list is
not, because you can add to it. Why it helps: if a value cannot change, no distant part of the
program can change it behind your back, which removes a whole family of confusing bugs, and
immutable data is safe to share freely.

**Functions as values (higher-order functions).** In this style a function is just another value:
you can put it in a variable and pass it to another function. A function that takes a function as
input, or returns one, is called a **higher-order function**. An everyday example is a sort that
takes a "how to compare" function, so you can sort by any rule you pass in.

**How it helps readability and maintainability.** Pure functions and immutable data remove the
"something changed and I cannot find where" problem. A chain of small transformations reads clearly
from top to bottom, and each piece can be tested on its own.

**The balance.** A real program must do side effects eventually: read files, print, call a database.
You do not have to be strict about being purely functional. The practical move is to keep the core
logic in small pure functions and immutable values, and push the side effects (input and output) to
the edges. Borrowing these ideas is enough to make code much simpler.

**SOLID link.** Pure functions and immutable data make Single Responsibility and testing natural,
because each function does one thing and depends on nothing hidden.

### 1.4 Metaprogramming

**What metaprogramming means.** Normal code works on data: numbers, text, lists. **Metaprogramming**
is code that works on **code**: it inspects, changes, or generates other code. The prefix "meta"
means "about itself", so metaprogramming is "programming about programming". It sounds advanced, and
the deepest parts are, but the common part is something you will use often.

**Why it exists.** Sometimes the same extra behaviour is needed by many different functions: timing
how long each one takes, logging each call, checking a permission, caching a result. Copying that
behaviour into every function is repetitive and easy to get out of step. Metaprogramming lets you
write it once and attach it where needed.

**Decorator.** A **decorator** is a wrapper you put around a function to add behaviour before and
after it, without changing the function's own code. For example, a `timed` wrapper can start a
clock, run the real function, stop the clock, and report the time, while the function itself stays
focused on its real job.

```python
import time

def timed(func):                       # a decorator takes a function
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)  # run the real function
        print(f"{func.__name__} took {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

@timed                                  # attach the wrapper: load_data = timed(load_data)
def load_data(): ...
```

The `@timed` line means "wrap `load_data` with `timed`". Now every call to `load_data` is timed, and
`load_data` itself never mentions timing. This is the metaprogramming tool you will actually use,
and it is the one we use later in this chapter.

**Properties and descriptors.** These let a small method run when you simply read or set what looks
like a plain attribute.

```python
class Account:
    def __init__(self, paise: int) -> None:
        self._paise = paise

    @property
    def rupees(self) -> float:    # looks like an attribute, but runs this method
        return self._paise / 100

acc = Account(12550)
print(acc.rupees)                 # 125.5 (no parentheses: reading it runs the method)
```

`@property` lets you read `acc.rupees` like a plain attribute while a method quietly computes it. A
**descriptor** is the lower-level tool that `property` itself is built on; you almost never write one
by hand. Handy in small doses; used a lot, it hides what is really happening.

**Metaclass.** A class is a blueprint for objects; a **metaclass** is a blueprint for classes, code
that builds or changes classes as they are defined.

```python
class AutoKind(type):             # a metaclass inherits from `type`, the maker of classes
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        cls.kind = name.lower()   # add an attribute to every class built with this metaclass
        return cls

class Order(metaclass=AutoKind):
    pass

print(Order.kind)                 # "order": set automatically when the class was created
```

`type` is the built-in that makes classes, and a metaclass customizes that step: here every class
that uses `AutoKind` gets a `kind` attribute for free. This is the deepest and rarest tool. Most
developers go years without writing one, and you almost never should, because a base class or a
decorator usually does the same job more clearly.

**How it helps.** It removes repetition for genuine **cross-cutting concerns**, meaning concerns
that cut across many parts of the code in the same way, such as logging, timing, or caching.

**The risk (important).** Every one of these tools hides behaviour behind something that does not
look like a normal function call. A reader sees `@something` above a function, or a plain-looking
attribute, and may not realize extra code runs. Overused, metaprogramming makes code clever and hard
to follow, which is the opposite of maintainable. The rule: use it only for a real cross-cutting
concern, and always reach for the plainest tool that does the job (a decorator before a metaclass).

**SOLID link.** A decorator that adds one cross-cutting concern keeps the wrapped function focused
on its single responsibility. A metaclass that hides ordinary logic works against readability.

We have now covered the four paradigms and their constructs in detail. Next we see how Python writes
each one.

---

## Part 2: The same constructs in Python

Python is a **multi-paradigm** language: it gives you all four styles above, and you mix them
freely. Here is how Python writes each construct, in the same order. This is also where we start
the reviews example: a small service that reads product reviews and reports how many there are and
how many distinct products they cover.

### 2.1 Dynamic in Python

Python is dynamically typed. A name is just a label and can point at any object.

```python
x = 42        # x names an int
x = "forty"   # now a str; legal, because the type belongs to the object, not the name
```

Duck typing means code calls the method it needs and works with any object that has it. To keep
the flexibility without the late errors, add **type hints** and run **mypy** (wired in on Day 1).
Hints do not change how Python runs; a separate checker reads them and finds mismatches before the
code runs.

```python
def average(values: list[float]) -> float:
    return sum(values) / len(values)

average(["1", "2"])   # mypy flags this before you ever run it
```

For the reviews example, we will name the shape of a data source with a type hint later, so any
object that can hand over rows fits, whatever its class.

### 2.2 Object-oriented in Python

**A class** is worth writing when it holds state that several methods share:

```python
class Tally:
    def __init__(self) -> None:
        self._total = 0

    def add(self, amount: int) -> None:
        self._total += amount

    def result(self) -> int:
        return self._total
```

> **Try it.** Run `poetry run python demo_class_vs_function.py`. A one-method `Discounter` class and
> a `discounted()` function both return `90.0`, so the class adds nothing there. A `Tally` that
> keeps a running total across calls prints `15`, the case where shared state does need a class.

**Dunder methods (the special `__name__` methods).** In the `Tally` class above you saw `__init__`.
Python has a set of special methods whose names start and end with two underscores, said "dunder"
(short for double underscore). You rarely call them yourself; Python calls them for you at the right
moment. (`self`, which they all take as the first argument, is just the object the method is working
on; Python passes it in automatically.) The common ones for a class:

- `__init__(self, ...)`: the **constructor**. Python runs it when you create an object, for example
  `Review("P1", 5)`, to set up the object's starting data.
- `__repr__(self)`: returns a **text form of the object for developers**, shown when you print it or
  look at it in a debugger. A good one shows enough to recreate the object, like
  `Review(product_id='P1', rating=5)`.
- `__eq__(self, other)`: defines what `==` means for two objects. Without it, `==` only checks
  whether they are the very same object in memory; with it, two reviews can count as equal when
  their fields match.

Other dunder methods you will meet: `__str__` (a friendlier text form for end users), `__hash__`
(lets an object be a dict key or go into a set), `__lt__` and its siblings (define `<` and `>` for
sorting), `__len__` (makes `len(obj)` work), `__enter__` and `__exit__` (let an object be used in a
`with` block, from Day 2), and `__post_init__` (a dataclass hook that runs right after `__init__`,
which we use on Day 4 to check a value). Writing these by hand for a data class is repetitive
and easy to get wrong, which is exactly why a dataclass writes them for you.

**A dataclass** is for data that travels together. It generates `__init__`, `__repr__`, and `__eq__`
from the fields you declare, and `frozen=True` makes it immutable, a safe value object:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Review:
    product_id: str
    rating: int
```

> **Try it.** Run `poetry run python demo_dataclass.py`. A hand-written class and a `@dataclass`
> print the same and compare equal, but the dataclass needed far less code. A frozen one then
> refuses a change with `FrozenInstanceError`.

**Composition** means an object holds another and uses it, instead of inheriting from it. A report
*has* a formatter it can swap:

```python
class Report:
    def __init__(self, formatter: Formatter) -> None:
        self._formatter = formatter   # composition: a report HAS a formatter

    def render(self, rows: list[str]) -> str:
        return self._formatter.format(rows)
```

> **Try it.** Run `poetry run python demo_composition.py`. Handing the same `Report` a plain
> formatter, then a bullet formatter, changes the output with no change to `Report` itself.

**A Protocol** gives polymorphism by shape. You declare a small interface, and any class with the
right method fits, with no base class to inherit (this is called structural typing):

```python
from collections.abc import Iterator
from typing import Protocol


class ReviewSource(Protocol):
    def rows(self) -> Iterator[dict[str, str]]: ...
```

> **Try it.** Run `poetry run python demo_protocol.py`. Two unrelated classes, `Money` and
> `Percent`, each have a `format()` method, so both fit one `Formatter` protocol with no shared
> base class, and one function accepts either.

### 2.3 Functional in Python

Functions are values you can pass around. Comprehensions and generators transform data top to
bottom, in constant memory (from Day 2). Immutability comes from a frozen dataclass or a tuple.

```python
ratings = [r.rating for r in reviews]       # a comprehension: build a list
total = sum(r.rating for r in reviews)      # a generator: no list held in memory
```

For the reviews example, turning a raw row into a `Review` is a small **pure function**:
the same row always gives the same `Review`, and it changes nothing else, so it is easy to test.

```python
def parse_review(row: dict[str, str]) -> Review:
    ...   # returns a Review built from a raw row
```

### 2.4 Metaprogramming in Python

A **decorator** is written with `@name` above a function. We use one small `@timed` decorator to
time the summary step, a cross-cutting concern kept in one place instead of copied into the method:

```python
@timed("summary")
def summarize(self) -> dict[str, int]:
    ...
```

> **Try it.** Run `poetry run python demo_decorator.py`. A `traced()` decorator prints a line
> before and after `add(2, 3)`, which still returns `5`. The tracing lives in one place, and
> `add()` was never touched.

**Properties and descriptors** make a method look like an attribute; use them rarely.
**Metaclasses** build classes; you almost never need one, and a plain base class or a decorator is
usually clearer.

We can now write every construct in Python. The last part is the rule for choosing among them.

---

## Part 3: Use a construct only if it fits

We know all of these constructs. We do not use one just because we know it. Each has a place where
it helps and a place where it only adds weight. The tables below are a quick check: use a construct
when the left side is true, and leave it out when the right side is. After the tables, we take the
reviews example from a rough first version to a clean one and watch each construct make it better
or worse.

### 3.1 When to use each object-oriented construct

| Construct | Use it when | Do NOT use it when |
| --- | --- | --- |
| class | it has data plus behaviour, shared state, or many instances | it has one method and a constructor: use a function |
| dataclass | a group of values travel together | it is a throwaway pair: a tuple is lighter |
| frozen dataclass | the value must not change after it is made | it genuinely has to change in place |
| inheritance | a true, stable "is-a", or defining an interface | you only want to reuse a method: use composition |
| composition | one object needs another to do a job | (this is the default; prefer it) |
| protocol | you want to swap or fake an implementation | there is only ever one implementation |
| decorator | one cross-cutting concern is shared by many functions | it would hide important control flow |

### 3.2 SOLID, as a quick check

| Principle | The do | The don't |
| --- | --- | --- |
| Single Responsibility | one class or function, one job | a function that reads, transforms, and prints |
| Open-Closed | add new behaviour by adding code | edit tested code for every new case |
| Liskov Substitution | a subclass works anywhere its parent does | a subclass that breaks the parent's promises |
| Interface Segregation | small, focused interfaces | one big interface nobody fully uses |
| Dependency Inversion | depend on a protocol and inject it | build your own file reader or client inside a class |

In Python, the two that do most of the work are **Single Responsibility** and **Dependency
Inversion**. The other three mostly take care of themselves once you prefer composition and small
protocols, so you rarely have to chase them.

### 3.3 Design patterns, only when they fit

| Pattern | Helps when | Skip it when |
| --- | --- | --- |
| Factory | object creation is complex or must live in one place | a plain constructor call would do |
| Strategy | you swap an algorithm (composition plus a protocol) | there is only one algorithm |
| Dependency injection | you want to test or swap a dependency | (rarely a mistake; usually worth it) |
| Singleton | you truly need exactly one shared instance | it is a global by another name: avoid it |

The rule behind the table is **YAGNI**, short for "you are not going to need it": build the
simplest thing that solves today's problem. An abstraction with a single use is a candidate to
inline back into the one place that uses it.

### 3.4 The reviews example, from rough to clean

Now put it together on one service. We start with the roughest version that works and improve it
one construct at a time, checking each change against the tables above.

**Step 0. The rough version.** A review is a plain dict, and one function does everything: read the
file, count, and print.

```python
def run(path):
    rows = list(csv.DictReader(open(path)))
    reviews = 0
    products = set()
    for row in rows:
        reviews += 1
        products.add(row["product_id"])
    print(reviews, len(products))
```

It works, but reading a file, counting, and printing are three jobs in one function (against
Single Responsibility), and a plain dict has no fixed shape, so a typo in a key fails only at run
time.

**Step 1. Give the data a shape.** Make a frozen `Review` dataclass.

*Better:* the shape is now explicit and fixed, and mypy checks every field
access. (Table 3.1: a group of values that travel together, use a dataclass.)

*What would make it worse:* wrapping the parsing in a one-method class `ParserService` with only a
`parse()` method. That adds ceremony and holds no shared state, so a plain function reads better.
(Table 3.1: one method and a constructor, use a function.)

> **Try it.** Run `poetry run python demo_dict_vs_dataclass.py`. A mistyped key on a dict is a
> run-time `KeyError` on read and silent junk on write; the same data as a dataclass has one
> declared, checkable shape.

**Step 2. Parse with a pure function.** `parse_review(row)` returns a `Review`. It is pure, so a
test can check it with no file and no setup.

**Step 3. Separate the jobs.** Split the one big function into three: a **source** that reads rows,
a **summary** that counts, and a thin **entry point** that prints. Now each part has one reason to
change (Single Responsibility), and you can test the counting without a real file.

**Step 4. Depend on a protocol, and inject it.** Define a `ReviewSource` protocol with a `rows()`
method. Write a `CsvReviewSource` for the real file and an `InMemoryReviewSource` for tests. The
service receives its source from outside instead of building one.

*Better:* a test can hand the service an in-memory list and check the result, with no change to the
logic. (Table 3.2: Dependency Inversion, depend on a protocol and inject it.)

*What would make it worse:* a deep tree `BaseSource` to `FileSource` to `CsvFileSource`. It is
rigid, and the behaviour spreads across the tree. Composition plus a protocol is flatter and
clearer. (Table 3.1: use composition, not inheritance, to reuse behaviour.)

> **Try it.** Run `poetry run python demo_dependency_injection.py`. A service that builds its own
> source is stuck with it (`60`); a service that receives its source runs the same logic with a
> real source (`60`) or a fake one (`3`), chosen only by what you pass in.

**Step 5. Add one decorator for a cross-cutting concern.** Put a small `@timed` on the summary
step, so timing lives in one place. (Table 3.1: one shared concern, use a decorator. A stack of
decorators that hides the logic would be the wrong call.)

**The finished shape.** A frozen `Review`, a `parse_review` function, a `ReviewSource` protocol
with two sources, a `SummaryService` with its source injected, and one `@timed` decorator. Each
piece has one job, and you can read or change any one of them without loading the whole thing into
your head. Every construct we kept made the code easier to read and change; the ones we turned down
(a one-method class, a deep inheritance tree) would have made it worse.

---

## Recap

- A paradigm is a way to organize code, and its constructs are the tools it gives you. Maintainable
  code uses the tool that fits and leaves out the rest.
- **Dynamic:** flexible; add type hints so mistakes show early. **Object-oriented:** bundle data and
  behaviour; prefer composition over deep inheritance. **Functional:** pure functions and immutable
  data are easy to test. **Metaprogramming:** powerful; use it only for a real cross-cutting concern.
- Before using a construct, check the when and when-not tables. Use SOLID and design patterns as a
  quick check, not a checklist, and follow YAGNI.
- On the reviews example, each construct we kept (dataclass, pure parse function, protocol,
  injection, one decorator) made the code simpler to read and change. Forcing a class or a deep
  inheritance tree would have made it worse.

The review checklist for the whole day: does each class need to exist, could inheritance be
composition, are dependencies injected or built inside, does any abstraction have more than one
real use, and are reading, logic, and printing kept apart? Those questions turn "it works" into
"it can be changed."

**Next:** the [live lab](live-lab.md) builds this reviews service for real, ending with a test that
swaps the data source without touching the logic. Then two offline assignments apply the same
design to IoT telemetry and to financial transactions.
