# Assignment 02 · A versioned contract and a resilient link for transactions-insight

> Offline practice for the Microservices Architecture topic. In class you split
> `reviews-insight` into services joined by a contract and an event, and you guarded the calls
> between them. Now run the same redesign on your `transactions-insight` service, with the
> emphasis the money domain calls for: the boundary between two services is a promise you
> version and keep, and a call that crosses it must survive the other service being slow or
> down. The pressure is correctness under failure: the ledger must reconcile, and the caller
> must degrade cleanly rather than hang.

This is a do-it-yourself assignment. The point is to feel two disciplines the money domain
makes non-negotiable. First, the contract between services is a versioned boundary: money is
carried as integer minor units, never a float, and the shapes both sides depend on live in one
place. Second, the link between services is resilient: a call has a timeout, a retry, and a
circuit breaker, so one failing service does not take its callers down, and the gateway returns
a clear answer instead of hanging. The counting is a running balance; what is new is that it
lives across a service boundary that must hold under failure.

Start from the `transactions-insight` domain: a transaction is an account id, an amount in
integer paise, and a kind (a credit or a debit). Build the split as its own project, mirroring
the reference structure from the live lab, and keep it offline: a file-backed broker stands in
for a real one.

## The goal

One thing, done honestly: two services joined by a versioned contract and an event, with a
resilient link and a ledger that reconciles. A `transactions-service` accepts and stores a
transaction and publishes a `transaction-recorded` event. A `ledger-service` consumes those
events into its own read store and serves a per-account summary (the count and the balance,
where a credit adds and a debit subtracts). A gateway calls the ledger through a resilient
client and degrades cleanly when it is down. The proof of the assignment is two behaviours: the
ledger balance reconciles against the transactions, and the gateway stays up when the ledger
does not.

The target behaviour, from the end-to-end run, is:

```text
ledger-service consumes the events and serves the account summary:
  /v1/accounts/acc-1/summary -> {'account_id': 'acc-1', 'count': 5, 'balance_cents': 8700}

reconciliation check (balance must equal credits minus debits, in paise):
  expected balance = 8700 (rupees 87.00)
  ledger balance   = 8700 (rupees 87.00)
  reconciled       = True

the gateway degrades cleanly when ledger-service is down:
  /bff/account/acc-1 -> 200 {'account_id': 'acc-1', 'summary': None, 'note': ...}

unknown account escalates to a clear 404, not a guess:
  /v1/accounts/unknown/summary -> 404
```

Run the redesign through the chapter's lens. For each piece, hold both halves in view:

- **Architecture.** The contract is a versioned boundary, so a change adds a field rather than
  breaking a caller. Money is exact, so it is carried as integer paise. The link is a remote
  call, so it assumes partial failure: a timeout, a retry, a circuit breaker, and a clean
  fallback.
- **Engineering.** Make the code hold the design: the contract is a set of pydantic models on a
  `/v1` path, amounts are integers throughout, the resilient client wraps every call, and the
  gateway returns a null summary with a note when the ledger is down.

## What you have to build

One Poetry project with a `src` layout and these packages, mirroring the live lab:

1. **The contract (`contracts/`).** `TransactionIn{account_id, amount_cents, kind}` where
   `amount_cents` is a positive integer and `kind` is a credit or a debit; `TransactionCreated
   {id}`; `AccountSummary{account_id, count, balance_cents}`; and the event
   `TransactionRecorded{id, account_id, amount_cents, kind}`. Money is integer paise, never a
   float.
2. **The shared infrastructure (`common/`).** Config, a correlation-id middleware with a health
   route, a file-backed broker with an idempotent `drain`, and a resilient client with a
   timeout, a retry, and a circuit breaker. Carry these forward from the live lab.
3. **`transactions-service`.** `POST /v1/transactions` validates and stores a transaction and
   publishes a `transaction-recorded` event; `GET /v1/transactions/{account_id}` lists an
   account's transactions. Use a versioned path.
4. **`ledger-service`.** Consumes `transaction-recorded` events idempotently into its own read
   store (a credit adds to the balance, a debit subtracts), and serves `GET /v1/accounts/
   {account_id}/summary`, returning a 404 for an unknown account.
5. **The gateway.** `GET /bff/account/{account_id}` calls the ledger through the resilient
   client, forwards the correlation id, and degrades cleanly when the ledger is down (a null
   summary with a note, status 200); `POST /transactions` returns a 502 when the transactions
   service is down.
6. **Tests** that prove each service, the contract and the end-to-end path, observability,
   reconciliation, resilience (the circuit breaker opens then recovers), and degradation.

## Staged guidance

Work in small stages; check each before moving on.

### Level 1: the versioned contract, with money as integers

Define the four models. Carry `amount_cents` as a positive integer everywhere, and make `kind`
a credit or a debit only. Put the routes on a `/v1` path, so a later change can add a `/v2`
without breaking a caller on `/v1`.

Hint: money in a float is a bug waiting to happen, because a value like 0.1 has no exact binary
form and rounding errors accumulate. Integer minor units (paise) are exact, and you format them
as rupees only when you show them to a person.

### Level 2: record transactions and reconcile the ledger

Build `transactions-service` to store and publish, and `ledger-service` to consume into a
per-account balance where a credit adds and a debit subtracts. The balance the ledger serves
must equal the sum of credits minus the sum of debits over the recorded transactions.

Hint: reconciliation is the money domain's version of a test. It is not enough that the code
runs; the balance must equal what the transactions say it should. Assert it: sum the credits
and debits yourself and compare to the ledger's balance.

### Level 3: the resilient link and graceful degradation

Wrap the gateway's call to the ledger in the resilient client: a timeout on every call, a retry
with backoff for a transient failure, and a circuit breaker that opens after a run of failures
and recovers after a cooldown. When the ledger is down, the dashboard returns a null summary
with a note, status 200, not a hang or a 500. When the transactions service is down, a submit
returns a clear 502.

Hint: the circuit breaker protects the caller, not the callee. Once the ledger is clearly down,
the breaker stops the gateway from throwing every request into it and exhausting its own
resources waiting on timeouts.

### Level 4: correlation id across the call

Stamp each request with a correlation id in a middleware, and forward it on the call from the
gateway to the ledger, so one request can be followed across both services in the logs.

Hint: with the id threaded through, a failed request that touched two services can be stitched
back into one story from the logs. Without it, you have two unrelated log streams and a guess.

### Level 5: prove it

Write the tests. Alongside per-service, contract, end-to-end, and observability tests, write the
two that define the assignment. A **reconciliation** test: record a mix of credits and debits
and assert the ledger balance equals credits minus debits, in integer paise. A **resilience**
test: with an injectable clock, show the circuit breaker opens after the threshold of failures
and recovers after the cooldown, and show the gateway degrades cleanly (a null summary with a
note) when the ledger is down and returns a 502 when the transactions service is down.

Hint: use a temp store and broker per test. For the breaker, inject the clock so you can advance
it past the cooldown without a real sleep, which keeps the test fast and deterministic.

### Level 6: green gate

```bash
poetry run pytest -q                     # all green
poetry run ruff check src tests scripts  # All checks passed!
poetry run mypy src                       # Success: no issues found
poetry run python scripts/smoke.py        # the end-to-end run, with the reconciliation check
```

## Done when

- [ ] Two services, `transactions-service` and `ledger-service`, each with its own store, plus a
  gateway, in one Poetry project with a `src` layout.
- [ ] The contract lives in a `contracts` package on a `/v1` path; money is integer paise
  throughout, never a float; `kind` is a credit or a debit only.
- [ ] The ledger consumes `transaction-recorded` events idempotently; a credit adds and a debit
  subtracts; an unknown account returns a 404.
- [ ] **Reconciliation holds:** the ledger balance equals credits minus debits, proven by a
  test and shown by the smoke script (balance 8700 paise for the sample run).
- [ ] The gateway's call is wrapped in the resilient client (timeout, retry, circuit breaker);
  the **breaker opens after repeated failures and recovers after a cooldown**, proven by a test.
- [ ] The gateway degrades cleanly when the ledger is down (a null summary with a note, status
  200) and returns a 502 when the transactions service is down.
- [ ] A correlation id is stamped and forwarded across the call.
- [ ] `pytest`, `ruff check`, and `mypy src` are all green, and `scripts/smoke.py` shows the
  summary, the reconciliation as `True`, and the clean degradation.

When every box is ticked, you have run the chapter's redesign over the money domain: a versioned
contract that carries money exactly, a resilient link that survives the other service failing,
and a ledger that reconciles. The worked solution is in `solution-02.md` if you want to compare,
but try first.
