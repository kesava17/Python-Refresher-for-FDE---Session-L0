# Artificial Neural Networks: An Introduction

> Strip away eighty years of decades and jargon, and every neural network is the same idea:
> learn from examples by adjusting the strength of connections. Show the network many examples,
> let it guess, measure how wrong it was, and nudge its connection weights to be a little less
> wrong next time. Repeat, millions of times. That one idea, first written down in 1943, runs
> unbroken through every model you will meet, up to the largest system in use today.

This is the opening chapter of the neural networks course, and you can read it on its own. It is
not a list of equations but the story of the field, told the way the field actually unfolded, so
that each idea arrives with a reason. We meet each concept at the moment it was invented, and follow
it forward to the tools you use now. No mathematics is assumed. The goal is a clear mental map: the
ideas, the order they came in, and why each one mattered.

One thing recurs so often that it is worth naming first. Progress came whenever one of three levers
caught up with the others: more **data** to learn from, more **compute** to learn with, and better
**algorithms** to learn by. Every winter in the story was a missing lever, and every spring was a
lever arriving. These three explain the long dry spells and the sudden breakthroughs better than any
single genius does, so watch for them throughout.

The chapter proceeds in the order history did: the idea is born (1943 to 1958), the first winter and
the problem a machine could not solve (1969), backpropagation and the revival (the 1980s), the quiet
years (the 1990s to the 2000s), deep learning breaks through (2006 to 2012), language and attention
and the Transformer (2013 to 2017), the generative era (2014 to now), where it goes next, and finally
the family of architectures. Along the way we pause on four hard problems that defined their eras:
whether a machine could learn to see, reading a nation's mail, the translation dream, and building a
machine you can just talk to. Each is a small scene, so you can picture the era, not just date it.

## Objective

By the end of this chapter you will be able to explain, in plain words and without any mathematics,
what a neural network is and how one learns. You will hold the whole arc of the field in your head:
the one idea behind all of it, the three drivers that gate progress, the two winters and the two
revivals, and the path from a single mathematical neuron to today's generative models. You will
know the name and the purpose of every major idea in the modern toolkit, so that when a later
topic opens one up in detail, you already know why it was invented and what it replaced. This is
the map that makes the mathematics make sense.

## Coverage

- The one idea (learning by adjusting connection weights) and the three drivers (data, compute,
  algorithms).
- The artificial neuron: inputs, weights, a sum, and an activation.
- The perceptron and its learning rule; linear separability and the XOR limit.
- Backpropagation and gradient descent, with the speed-ups that make training practical:
  stochastic gradient descent, momentum, and Adam.
- Depth and representation learning; convolutional networks (CNNs) for images.
- The recurrent family for sequences: RNN, LSTM, and GRU, and the vanishing-gradient problem.
- The deep-learning toolkit that made depth trainable: ReLU, dropout, and batch normalization.
- Embeddings (meaning as vectors), attention, and the Transformer.
- The generative era: GANs, diffusion, foundation models, scaling, and large language models.
- The frontier and the honest limits, and the family of neural architectures as a whole.

---

## Part 1: the idea is born (1943 to 1958)

### 1943: a neuron, written as mathematics

Two researchers, Warren McCulloch and Walter Pitts, asked a bold question in 1943. Could the
brain's neurons be described as logic? A biological neuron receives signals from other neurons,
and when the combined signal is strong enough, it fires and passes a signal on. McCulloch and Pitts
proposed a stripped-down version of this in arithmetic. Their **artificial neuron** takes several
inputs, weighs each one (some inputs matter more than others), adds them up, and fires if the total
passes a **threshold**. A weight is simply a number that says how much an input counts. A threshold
is the level the total must reach for the neuron to fire. That is the whole unit: a tiny decision
maker, written in numbers.

Why did this matter so much? It was the first serious claim that thought could be computed. If a
neuron is nothing more than weighted inputs and a threshold, then a network of these units could, in
principle, compute anything that logic can. Every network in this course, up to the largest model in
the world today, is built from this one unit repeated at scale. If you carry a single picture out of
this chapter, carry this one.

Here is that picture in words. Inputs come in, each is multiplied by its weight, and the results are
added together. An **activation** (the rule that decides the output from the total) then produces the
neuron's output. Written out, one neuron computes:

```
output = activation( w1*x1 + w2*x2 + ... + wn*xn + bias )
```

The x values are the inputs you are handed by the problem. The w values, the weights, are what the
network learns. The **bias** is one extra number that shifts the threshold, making the neuron
easier or harder to fire. Read that line once more, because it is the entire game in miniature. The
inputs are fixed by the problem. The weights are the knowledge. Everything that follows in the next
eighty years is a better way to find good weights.

> **Try it.** Run `poetry run python demo_neuron.py` in the demos folder. With weights `[1, 1]` and
> bias `-0.5`, the neuron behaves like a logical OR: it fires unless both inputs are zero. Change
> only the bias to `-1.5` and the very same neuron now behaves like AND: it fires only when both
> inputs are one. Nothing changed but one number, and the logic changed with it. Learning is finding
> those numbers automatically, instead of setting them by hand.

### 1949: how connections could learn

The neuron could compute, but nothing yet said how it would learn. Donald Hebb gave the first
answer in 1949, and he took it from biology. His rule is usually summarized as neurons that fire
together, wire together. When two connected neurons are active at the same time, strengthen the
connection between them. Learning, in this view, is a change in connection strength, nothing more
mysterious than that.

The importance of Hebb's rule is that it made learning mechanical. Learning was no longer a mystery
reserved for living brains; it was a rule for adjusting weights from experience. A network does not
store facts in its cells the way a filing cabinet stores paper. It stores them in the strengths of
its connections. That idea, that weights change with use, is still the beating heart of training
today.

### 1958: the perceptron, a machine that learns

In 1958, Frank Rosenblatt built the first neural network that could actually be trained from
examples, and the world took notice. His **perceptron** was a neuron fitted with a learning rule.
The rule is simple and worth understanding, because it is the ancestor of all the training methods
that come later. Show the perceptron an example. Let it make a guess. Compare that guess to the
correct answer. If it was right, leave the weights alone. If it was wrong, adjust each weight a
little, up or down, in the direction that would have made the guess better. Do this over many
examples, again and again, and the perceptron gradually settles on a set of weights that classifies
the examples correctly. It learned the weights; nobody set them by hand.

Rosenblatt built this as real hardware, the room-sized Mark I Perceptron, to recognize simple
shapes. The press ran far ahead of the science, announcing a machine that would soon walk, talk,
and be conscious. This gap between the promise and the reality is a pattern you will see repeat.
The genuine achievement, though, was real: the perceptron performed **pattern recognition**,
telling one simple image from another, and it is the direct ancestor of every classifier since.

> **Try it.** Run `poetry run python demo_perceptron_or.py`. Watch the mistakes fall epoch by epoch
> (an epoch is one pass through all the examples) until, around epoch 7, the perceptron reaches 100
> percent accuracy on OR and stops. The final weights were learned from the four examples alone. No
> person wrote them.

### The problem of the day, circa 1958: can a machine learn to see?

Picture a laboratory at the Cornell Aeronautical Laboratory. A room-sized machine, the Mark I
Perceptron, stares at cards through a grid of four hundred light sensors and slowly learns to tell
one shape from another. The US Navy is paying for it, hoping for machines that can read photographs
and spot patterns no human has time to check.

The hard problem was this. Recognizing a shape, a letter, a face, is effortless for a person and
was impossible for a computer. Every rule an engineer wrote by hand to describe a letter broke on
the next handwritten example. The perceptron offered a different path. It did not need the rules.
Shown enough labelled examples, it adjusted its own weights until it could classify them. The
machine learned the pattern instead of being told it. That was genuinely new.

But a fresh limit appeared almost immediately. The perceptron could only separate classes that a
straight line could divide. Anything more tangled than that, it could not learn, and this limit was
about to stop the field cold. Notice the shape of this scene, because it is the shape of the whole
story: a hard human problem, a network that learns instead of being programmed, and a new limit
that becomes the next chapter's quest.

---

## Part 2: the first winter (1969)

### 1969: the problem the perceptron could not solve

In 1969, Marvin Minsky and Seymour Papert proved a hard limit, and the consequences were severe. A
single-layer perceptron can only separate two classes with one straight line. This is called
**linear separability**: a problem is linearly separable when a single straight boundary can put
one class on one side and the other class on the other side. OR is linearly separable, which is why
the perceptron learned it. Some problems are not, and the famous example is **exclusive-or**, or
XOR. XOR outputs 1 when its two inputs differ and 0 when they are the same. Plot the four cases and
you find the two ones sit on one diagonal and the two zeros on the other. No single straight line
can separate them. A perceptron has exactly one line to work with, so it can never solve XOR, no
matter how long it trains.

Minsky and Papert's book, *Perceptrons*, made this limit famous. Confidence collapsed, funding
dried up, and neural networks entered their **first winter**, roughly a decade of neglect. The
concept to hold onto is linear separability: one layer draws one straight boundary, and real
problems are rarely straight, so one layer is not enough.

> **Try it.** Run `poetry run python demo_xor_fails.py`. You will see the accuracy stall at 75
> percent (the best it ever reaches), because one straight line cannot separate XOR. One of the
> four cases is always on the wrong side. Raise the number of epochs to 500 if you like; it still
> cannot solve XOR, and that is the whole point.

### The fix everyone could see, and no one could train

The escape route was known in principle even then: stack the neurons in **layers**. Put one or more
**hidden layers** between the input and the output. A hidden layer is a layer of neurons that sits
in the middle, connected to neither the raw input nor the final answer directly. Each layer bends
the decision boundary a little more, so a stack of layers can carve out any shape at all, including
XOR. The power of layered networks was never really in doubt.

The trouble was training them. Nobody had a reliable way to decide how to adjust the weights of the
hidden layers. For the output layer you can see the error directly, because you know the correct
answer. But for a neuron buried in the middle, how much of the final error was its fault? Without an
answer to that question, deep networks were a dead end, and they stayed one for years.

---

## Part 3: backpropagation and the revival (the 1980s)

### 1986: backpropagation, teaching the hidden layers

In 1986, David Rumelhart, Geoffrey Hinton, and Ronald Williams popularized the algorithm that broke
the logjam: **backpropagation**. The idea is elegant. Make a guess and measure the error at the
output, as before. Then propagate that error backward through the layers, using calculus to work
out how much each individual weight contributed to it. Once you know each weight's share of the
blame, you nudge every weight, hidden ones included, in the direction that reduces the error. Repeat.

This changed everything, because now the hidden layers could be trained. Networks could be made
**deep**, meaning they could have many layers, and a deep enough network can approximate almost any
relationship between input and output. Three concepts arrive together here and are worth naming.
**Gradient descent** is the idea of rolling downhill on the error. The **chain rule** from calculus
is what lets the error be shared fairly across the layers. And **non-linear activations** (activation
rules that are not just straight lines) are what let stacked layers do genuinely more than a single
layer ever could. Without a non-linear activation, stacking layers gains you nothing, because a
stack of straight lines is still just a straight line.

### Gradient descent, and making it practical

Backpropagation tells each weight which way to move. **Gradient descent** is the rule for actually
moving them, and a great deal of the craft of training a network lives right here. The everyday
picture is a landscape. Imagine the error as a hilly terrain and the network's weights as your
position on it. The **gradient** is the direction of steepest uphill. So you step a little downhill,
again and again, and you gradually settle into a low-error valley. How big each step is called the
**learning rate**, and it turns out to matter enormously. Too small and training crawls. Too large
and you leap clean over the valley and bounce further out with every step.

Plain gradient descent works, but three refinements made it fast and stable enough for real use, and
you will use all three in practice:

- **Stochastic gradient descent (SGD)**: instead of measuring the error over the whole dataset
  before each step, update from small batches of examples at a time. This is faster and it scales to
  huge datasets, which is why it became the default.
- **Momentum**: keep some of your speed from the previous steps, so you roll steadily in a consistent
  direction and push through flat spots and small bumps instead of getting stuck in them.
- **Adam** and similar adaptive optimizers: automatically tune the step size separately for each
  weight, so you do not have to hand-pick one learning rate for the whole network. Adam is a common
  default today.

The concept underneath all of this is **optimization**: a network learns by descending an error
surface, and your choices of batch size, learning rate, and momentum decide whether it learns
quickly, slowly, or not at all.

> **Try it.** Run `poetry run python demo_gradient_descent.py`. With a sensible learning rate of
> 0.1, the value glides steadily toward the lowest point. With a learning rate of 1.1, it overshoots
> and flies apart, the error growing with every step. Somewhere near 1.0 the behaviour flips from
> converging to diverging, which is exactly the knife-edge you learn to feel for when you train a
> real model.

### Why depth is powerful

Backpropagation made depth trainable, and depth is what lets a network build understanding in
stages. Early layers learn simple patterns. Later layers combine those into more complex ones. For
an image, the first layers might detect edges, the next assemble edges into shapes, and later layers
assemble shapes into objects. Crucially, the network **discovers** these useful features by itself,
from the raw data, instead of being told what to look for.

This is the shift that defines the modern field, and it has a name: **representation learning**. You
stop hand-designing the features a model should pay attention to and let the network learn its own
representations directly from raw data. Give it enough examples and enough depth, and it often finds
structure a human would have missed. The driver behind this era was cognitive science, which pictured
the brain as a network of simple units learning together. Early applications included a system that
learned to pronounce written English aloud, and the first real handwritten digit recognition, which
brings us to the next scene.

### 1989 to 1998: networks that see

Yann LeCun, working through the late 1980s to 1998, built a network shaped specifically for images
and put it to work reading the mail. His **convolutional network** (a CNN) rests on a clever
observation. A fully connected network wires every pixel to every neuron, which is wasteful, because
a useful feature like an edge can appear anywhere in the picture. Instead, slide a small **filter**
(a little pattern detector) across the whole image to find that feature wherever it sits. Share the
same weights across the entire image, so the network learns once that an edge is an edge, rather than
relearning it separately in every corner.

The application was concrete and valuable. LeCun's LeNet read **handwritten digits** on cheques and
postal codes, at scale, in real production systems. The well-known MNIST dataset comes from this line
of work. It was one of the very first neural networks to earn its keep in the real world. Three
concepts crystallized here and are still central to computer vision: **convolution** (a filter that
finds a feature anywhere), **weight sharing** (learn a pattern once and reuse it everywhere), and
**translation invariance** (recognize a feature no matter where in the image it appears).

### The problem of the day, circa 1990: reading a nation's mail

Every day, post offices and banks drown in handwriting. There are millions of envelopes to sort by
postal code and millions of cheques to read by hand, and no two people write a seven the same way. At
Bell Labs, Yann LeCun pointed a convolutional network at the problem.

The hard problem was to read handwritten digits reliably, at industrial scale, when every sample is a
little different and a wrong read costs real money. The convolutional network learned the features of
a digit, a stroke, a loop, a corner, wherever they appeared, and read digits well enough to deploy.
For years it read cheques by the millions across the banking system. This was a neural network leaving
the laboratory and doing real work, for the first time.

The win, though, was narrow. It worked on clean, cropped digits. Photographs of the real world,
cluttered and varied, were still far out of reach, and training on them would need far more data and
compute than existed in 1990. That gap, between clean digits and messy natural images, defined the
next twenty years.

### 1997: networks that remember

Images are still pictures, taken in at a glance. Language, speech, and time are **sequences**, which
arrive one step at a time, and sequences need memory. A **recurrent network** (an RNN) provides it by
feeding its own output back in as part of the next input, so it carries a running memory of what came
before. Plain RNNs, though, forgot too quickly. In 1997 Sepp Hochreiter and Jurgen Schmidhuber fixed
this by adding **gates**, small learned controls that decide what to keep and what to discard. Their
design is the **LSTM** (long short-term memory), and a later, simpler cousin is the **GRU** (gated
recurrent unit). Both use gates to hold onto important information across many steps.

The gates were a fix for a deeper trouble called the **vanishing gradient**. In a deep or long
network, the error signal travelling backward during training can shrink toward nothing, so the early
layers barely learn at all. The LSTM's gates were an early and clever way around it. The problem
itself, though, returns later in the story. For years, the LSTM was the workhorse of anything that
arrived one step at a time: speech recognition, handwriting, and machine translation all ran on it.

---

## Part 4: the quiet years (the 1990s to the 2000s)

Backpropagation worked, but training deep networks in this period was slow, finicky, and starved of
both data and compute. Several forces pushed neural networks out of fashion:

- There was too little **data** to feed a hungry deep network.
- There was too little **compute**: training took days for modest results.
- The vanishing-gradient problem made real depth hard to train.
- Rival methods, especially support vector machines, were faster and often more accurate on the
  problems of the day.

So the field went quiet. But it did not stop. A small group, including Geoffrey Hinton, Yann LeCun,
and Yoshua Bengio, kept improving the ideas through the lean years. And notice the pattern once more.
Two of the three levers, data and compute, were simply missing. The algorithms were running ahead of
the hardware and the datasets. That gap was about to close, and when it did, everything changed at
once.

---

## Part 5: deep learning breaks through (2006 to 2012)

### The three drivers converge

Around 2010, the missing pieces arrived together, which is why this is the moment the modern era
begins. On **data**, the internet had produced huge labelled datasets, and in particular ImageNet
gathered millions of labelled images, a proper test of learning at scale. On **compute**, graphics
processing units (GPUs), originally built to render video games, turned out to be ideal for the
parallel arithmetic that neural networks require, cutting training time from weeks to days. On
**algorithms**, better activations (chiefly ReLU), better regularization (chiefly dropout), and
smarter ways of setting the starting weights finally made deep networks train reliably. None of these
alone was enough. Together, data, compute, and algorithms crossed a threshold, and deep networks went
from also-ran to unbeatable.

### 2012: AlexNet, the moment deep learning won

A single result ended the argument. In the 2012 ImageNet contest, Alex Krizhevsky, Ilya Sutskever,
and Geoffrey Hinton entered a deep convolutional network trained on GPUs. It did not merely win. It
cut the image recognition error rate almost in half, far beyond every hand-engineered rival. The
shock was clear and immediate: with enough data and compute, learned features beat hand-designed ones,
decisively. Within a year, the entire field of computer vision switched to deep learning. Object
detection, face recognition, medical imaging, and the perception systems in self-driving cars all
followed from this one door opening. The deep learning decade had begun.

### The toolkit that made depth train

AlexNet, and the wave of work right after it, was not one trick but a bundle of them. These methods,
most now standard, are what finally made deep networks train reliably, and you will reach for them in
almost every network you build. They fall into two groups.

Keeping a healthy signal flowing through the layers:

- **ReLU** (rectified linear unit): a simple activation that passes positive values through unchanged
  and clamps negatives to zero. It keeps the gradient alive through many layers and cures much of the
  vanishing-gradient problem, which is why it replaced the older, gentler activations.
- **Batch normalization**: steady the numbers flowing through each layer during training, which makes
  training both faster and more stable.
- Careful **weight initialization**: starting the weights at sensible values instead of arbitrary ones,
  so training begins on solid ground.

Helping the network generalize (perform well on new data, not just memorize the training set):

- **Dropout**: randomly switch off a fraction of the neurons during each training step, so the network
  cannot lean too heavily on any single one. This reduces **overfitting**, which is when a model learns
  the training examples so exactly that it fails on anything new.
- **Adam** and similar optimizers that adapt the step size for each weight.
- Plenty of labelled **data** and the **GPUs** to make use of it.

The concept here is **regularization and optimization**. Depth was always powerful in theory; these
are the practical methods that made it trainable in fact.

---

## Part 6: language, attention, and the Transformer (2013 to 2017)

Vision was solved well enough to trust. Language was next, and it needed a new idea.

### The problem of the day, 1954 to 2016: the translation dream

In 1954, a computer translated a set of Russian sentences into English and made headlines. The
language barrier, it was said, would fall within a few years. It did not. For half a century,
translation defeated hand-written rules and word-by-word statistics alike, because meaning does not
live in single words. It lives in whole sentences, where a word's sense depends on other words that
may sit far away, and where the natural word order differs from one language to the next.

The eventual breakthrough came from **attention**, which let a model look across the whole sentence
and focus on the words that mattered for each word it was producing. Translation quality jumped, and
by 2016 the large translation services had switched to neural models. But attention, at first, was
bolted onto slow, step-by-step recurrent networks. That raised a tantalizing question: could a network
be built from attention alone, and trained in parallel at scale? The answer opened straight onto the
Transformer and everything after it.

### 2013: meaning as numbers

Before a network can work with language at all, it needs to turn words into something it can compute
with. The 2013 idea that made this practical, popularized under the name word2vec, is the **word
embedding**. Represent each word as a short list of numbers, a **vector**, and learn those numbers so
that words with similar meanings end up near each other in the space. King and queen land close
together. King and apple land far apart. Strikingly, the arithmetic even captures relationships: king
minus man plus woman lands near queen.

The importance of this is that meaning became **geometry**. Once words are points in a space,
similarity becomes distance, and a network can reason about relationships with simple arithmetic. This
same idea, turning text (and later images, audio, and almost anything) into vectors so that similarity
becomes distance, underlies modern search, translation, and the retrieval that grounds today's
assistants. You will meet embeddings again and again.

> **Try it.** Run `poetry run python demo_embeddings.py`. It scores word pairs from 1.00 (same meaning)
> to 0.00 (unrelated). You should see king versus queen score 1.00 and king versus apple score 0.00,
> with king versus man in between. Real embeddings are learned and have hundreds of numbers each, but
> this toy version shows the exact idea: meaning laid out as distance.

### 2014: attention, focusing on what matters

Sequence models read one step at a time and struggled to hold a long input in memory, because
everything had to be squeezed into a single fixed memory as the model went. **Attention**, introduced
around 2014, gave them a way to look back. Instead of compressing the whole sentence into one memory,
the network can **attend** to the most relevant input words for each output word it produces.
Translating the word bank, it can look back at river or at money and choose the right sense.

This mattered for two reasons. Attention let models handle long inputs without forgetting the start by
the time they reached the end, and it made their choices easier to interpret, since you could see what
the model was looking at. Attention quickly became the most important tool in sequence modelling, and
it set the stage for the idea that would reshape the entire field.

### 2017: Attention Is All You Need

In 2017, a single paper proposed dropping recurrence entirely and building a network out of attention
alone. The result, the **Transformer**, is the architecture behind nearly everything modern. Its core
mechanism is **self-attention**: every word in the input looks at every other word at once and decides
how much to pay attention to each. Because there is no step-by-step recurrence, the whole sequence can
be processed in **parallel**, all at the same time.

That parallelism is why it took over. It made training fast on modern GPU hardware, and, just as
important, the Transformer kept getting better as it was made larger. It **scales**, and scaling is
what the next part is all about. If you remember one architecture from this course, remember this one:
every large language model, image generator, and multimodal system in use today is, at its core, a
Transformer.

---

## Part 7: the generative era (2014 to now)

Networks stopped only recognizing the world and started creating it. One distinction makes the rest of
the story clear.

### Two ways to use a network

A **discriminative** model tells things apart. Given an input, it predicts a label: is this a cat or a
dog, is this email spam? Everything up to this point, from the perceptron to AlexNet, was mostly of this
kind. A **generative** model instead learns the pattern of the data well enough to produce new examples
of it: it can write a sentence, paint an image, or compose audio. The difference is vivid: a
discriminative model can recognize a cat, while a generative model can draw a cat it has never seen.
That generative capability is what the public now simply calls "AI".

### 2014 to 2022: learning to generate images

Two families of ideas taught networks to create pictures. The first, from 2014, is the **generative
adversarial network** (GAN), Ian Goodfellow's idea. Pit two networks against each other. One, the
generator, produces fakes. The other, the discriminator, tries to spot them. They improve together, a
forger and a detective sharpening each other, until the fakes are convincing. The first striking
machine-made human faces came from this approach.

The second family, **diffusion**, matured between 2020 and 2022. Start from pure random noise and
remove it a little at a time, step by step, until a clean image emerges, all guided by a text prompt
describing what to draw. Diffusion powers the tools that put image generation in everyone's hands,
including DALL-E, Stable Diffusion, and Midjourney. In under a decade, machine-made images went from
blurry curiosities to results often indistinguishable from photographs, and the same approach now
reaches into video.

### Foundation models and the scaling insight

The Transformer set off a simple but powerful realization. Do not build a separate model for each task.
Instead, train one large model on a vast amount of general data, a **foundation model**, and then adapt
that single model to many specific jobs, either with a little extra training or with nothing more than a
well-chosen prompt. One model, many uses. Alongside this came the **scaling laws**: researchers found
that more data, more compute, and larger models keep producing better results in a fairly predictable
way. "Just make it bigger" worked far longer than anyone expected.

The concept underneath is **transfer learning** at scale. Knowledge learned once, from a huge and
general slice of data, transfers to almost any task. This is precisely why a single model can write
code, summarize a report, and answer a question, without being purpose-built for any one of them.

### The problem of the day, 1950 to 2022: a machine you can just talk to

In 1950, Alan Turing asked whether a machine could hold a conversation well enough to pass for human.
In 1966, a simple program called ELIZA echoed people's words back to them as questions, and some
people were convinced it understood them. It did not. General, open-ended language stayed out of reach
for another fifty years.

The hard problem was never a scripted chatbot. It was a system that genuinely handles open language:
questions, instructions, and reasoning, on any topic. The path to it ran through three ideas already in
this chapter. A Transformer, trained simply to predict the next word at enormous scale, absorbed
grammar, facts, and patterns of reasoning from a vast slice of text. Tuned afterward to follow
instructions, it became a general assistant. Turing's question took seventy years and three ideas from
this chapter, embeddings, the Transformer, and scale, to answer in practice. The new challenge is honest
and open: such a system is fluent, and it can be confidently wrong. Making it reliable, honest, and safe
is the live problem of the moment.

### 2022: the generative AI moment

Large language models had been growing quietly for several years. Then, in late 2022, one product put
them in front of everyone at once. A **large language model** is a Transformer trained to predict the
next word across a large slice of the internet; in doing so it learns grammar, facts, reasoning
patterns, and style. Tuned to follow instructions and human feedback, it becomes a general-purpose
assistant. And past a certain scale, these models began to show **emergent abilities**, things they
were never directly taught: translating, writing code, explaining a joke, solving a word problem.
Capability emerged from scale.

The public arrival was sudden. ChatGPT reached a hundred million users in weeks. Within a year, writing,
coding, customer support, tutoring, and search had all been touched. The technology had left the
laboratory and entered daily life.

### Beyond text: one method, many worlds

The same core ideas, embeddings and Transformers and scale, reached far past chat. In science,
**AlphaFold** predicted the three-dimensional shape of proteins, a decades-old grand challenge,
accelerating biology and medicine. In games, **AlphaGo** beat the world's best Go player in 2016,
learning strategies no human had taught it. And multimodal models now handle text, images, audio, and
video together, describing a picture or answering a spoken question with one system. The vindication
came in 2024, when the field's founders were honoured with Nobel Prizes: John Hopfield and Geoffrey
Hinton in physics for foundational work on neural networks, and the AlphaFold team in chemistry. An idea
dismissed twice was now reshaping science itself.

---

## Part 8: where the story goes next

We are in the middle of this chapter of history, not at its end. Four directions are moving fast and,
together, they define the next couple of years. First, **agents that act**: models moving from answering
questions to taking actions, using tools, browsing, and writing and running code to complete multi-step
tasks on your behalf. Second, **reasoning**: models trained to think before they answer, working through
a problem step by step, which sharply improves mathematics, coding, and planning. Third, **multimodal
and embodied** systems: one assistant that sees, hears, and speaks, and increasingly robotics that act in
the physical world. Fourth, **smaller and cheaper** models, efficient enough to run on a laptop or a
phone, bringing capable AI on-device, private, and low-cost.

A clear-eyed view of the limits matters as much as the excitement. The honest open problems include
**reliability** (models can state falsehoods with total confidence), **cost and energy** (training and
running large models is expensive), and **data** (the supply of fresh, high-quality training data is
finite). Alongside those sit the responsibilities we owe the technology: **alignment and safety**
(making systems do what we actually intend), **fairness and privacy** (whatever the data carries, the
model inherits), and **judgement** (a human stays responsible for the outcome). These are not reasons
to look away; they are the work, and the people who understand both the power and the limits are the
ones who will build trustworthy systems. What is certain is that the one idea from 1943, learning by
adjusting connections, is nowhere near the limit of what it can do.

---

## The family of neural architectures

The story produced a toolbox of network types, each shaped for a kind of data or a kind of job. This is
the map of what you will learn to build, and the reassuring part is that every one of them is the same
neuron and the same learn-by-adjusting-weights idea, arranged differently.

| Architecture | Best for | Key idea |
| --- | --- | --- |
| Multilayer perceptron (MLP) | tabular data, the basics | fully connected layers |
| Convolutional network (CNN) | images and grids | shared filters, local features |
| Recurrent network (RNN, LSTM, GRU) | sequences and time series | a memory of the past |
| Transformer | language, and now almost everything | self-attention, parallel, scalable |
| Autoencoder and VAE | compression and generation | encode to a small code, decode back |
| GAN | generating images | a generator and a critic compete |
| Diffusion model | high-quality image and video | generate by removing noise step by step |

Learn the core, and each architecture becomes a variation on a theme you already understand.

Here is the same journey as a timeline, every concept and the moment it entered the story:

| Year | Idea | Concept it introduced |
| --- | --- | --- |
| 1943 | the artificial neuron | weighted inputs, a sum, an activation |
| 1958 | the perceptron | learning weights from examples |
| 1969 | the XOR limit | linear separability, the need for depth |
| 1986 | backpropagation | gradient descent, training hidden layers |
| 1989 to 1998 | convolutional networks | filters, weight sharing, learned features |
| 1997 | LSTM | memory for sequences |
| 2012 | AlexNet | depth plus data plus GPUs |
| 2013 | word embeddings | meaning as vectors |
| 2017 | the Transformer | self-attention, scaling |
| 2014 to 2022 | GANs and diffusion | generating images |
| 2022 | large language models | foundation models, emergent ability |

---

## The build

The demos above each isolate one idea. The **live lab** puts three of them together into one small,
readable program. It is a package called `tinynn`, written in pure Python with no third-party
libraries, so you can read every single weight update and see exactly how a network learns. It contains
a neuron (a weighted sum through a step), a **perceptron** that learns its own weights, and a
**two-layer network** trained by backpropagation. One command runs the whole story:

```bash
poetry run python -m tinynn.run
```

and it prints three lines that are this entire chapter in miniature:

```text
perceptron on OR : converged at epoch 7, accuracy 100%
perceptron on XOR: accuracy 50%, it cannot reach 100 percent
two-layer on XOR : accuracy 100%, loss 0.0004
```

The perceptron learns OR from examples alone, because OR can be split by one straight line. It cannot
learn XOR, because no single line separates it: this is the wall of 1969. Add one hidden layer, train it
with backpropagation, and the very same problem is solved: this is the step that ended the first winter
and opened the road to deep learning. The lab is verified and its 8 tests pass, covering the datasets,
the perceptron, and the two-layer network, so you can trust the code you are reading and then change it
with confidence.

Two offline assignments take it further. The first, "the perceptron and the wall", runs the perceptron
across AND, OR, and XOR and asks you to see exactly where a single perceptron stops and why. The second,
"cross the wall, and size the hidden layer", trains the two-layer network on XOR and explores how many
hidden neurons it takes to solve the problem reliably. Both use the same `tinynn` package, so the code
you read in the lab is the code you experiment with in the assignments.

---

## Recap

Read the chapter back as one idea: **a neural network learns from examples by adjusting the strength of
its connections, and the whole history of the field is the story of finding better ways to do that,
gated at every turn by three drivers: data, compute, and algorithms.**

- **The one unit.** The artificial neuron of 1943: inputs, weights, a sum, and an activation. Every
  network is this unit repeated.
- **The first learner and its wall.** The perceptron of 1958 learned its weights from examples but could
  only draw one straight line, so XOR defeated it in 1969, and the field went quiet for a decade.
- **The revival.** Backpropagation in 1986 trained the hidden layers, gradient descent (with SGD,
  momentum, and Adam) moved the weights, and depth let networks learn their own features. CNNs learned
  to see; the RNN, LSTM, and GRU family learned to remember sequences.
- **The breakthrough.** Around 2012, data, compute, and algorithms converged. AlexNet won ImageNet, and
  the toolkit of ReLU, dropout, and batch normalization made depth reliably trainable.
- **Language and the Transformer.** Embeddings turned meaning into geometry, attention let models focus,
  and the 2017 Transformer, built on self-attention and trained in parallel, became the architecture
  behind almost everything modern.
- **The generative era.** GANs and diffusion learned to create images, foundation models and scaling laws
  turned one big model into a general tool, and large language models brought all of it into daily life
  in 2022, with AlphaFold and the 2024 Nobel Prizes as the vindication.
- **The honest close.** The frontier (agents, reasoning, multimodal, on-device) is real, and so are the
  limits (reliability, cost, data, safety). Both are the work.

You do not have the mathematics yet, but you have the map, which is what makes the mathematics make
sense. When a later topic opens up backpropagation, or convolution, or attention, you will already know
why it was invented and what it replaced.

**Next:** we open up that first neuron and the perceptron in depth, and train one ourselves in earnest.
The mathematics starts here, and now you know exactly why it matters.
