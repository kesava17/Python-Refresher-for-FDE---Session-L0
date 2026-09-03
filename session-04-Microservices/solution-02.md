# Solution 02 · A versioned contract and a resilient link for transactions-insight

> The worked solution for Assignment 02. Try the assignment yourself first. This walks the
> reference build in `code/microservices-architecture/assignment02`, which is verified: 20 tests
> pass, ruff and mypy strict are clean, and the smoke script runs end to end with a
> reconciliation check. There is no single correct set of names; there is a correct shape, and
> two behaviours that must hold: the ledger reconciles, and the gateway survives the ledger
> being down.

The assignment is not really about the arithmetic of a balance. It is about a boundary between
two services that must hold under two pressures the money domain always brings: a change to the
contract that must not break a caller, and a failure of one service that must not take the other
down. So the grading is on those two disciplines as much as the result: a trainee whose money is
exact, whose contract is versioned, and whose caller degrades cleanly has learned the thing.

## What a strong build shows (the rubric)

| Criterion | What earns the mark |
| --- | --- |
| **Money is exact** | amounts are integer paise everywhere, never a float; rupees appear only when a value is shown to a person. |
| **A versioned contract** | the shapes live in one `contracts` package on a `/v1` path, so a later change adds rather than breaks. |
| **The ledger reconciles** | the balance equals the sum of credits minus debits, asserted by a test, not assumed. |
| **A resilient link** | every call has a timeout and a retry, and a circuit breaker opens after repeated failures and recovers. |
| **Graceful degradation** | the gateway returns a null summary with a note when the ledger is down, and a 502 when the transactions service is down. |
| **Traceable** | a correlation id is stamped and forwarded across the call. |

The trap this assignment exists to catch is the call with no guard. It is easy to make the
gateway read the ledger with a plain client, and it works perfectly until the ledger is slow.
Then the gateway hangs on every request, its threads fill with waiting, and one failing service
has taken its caller down too. The discipline is to wrap the call: a timeout so it fails fast, a
retry for a blip, a breaker so a dead dependency is left alone, and a clean fallback.

## The reference build

The project mirrors the live lab, with the domain shifted to transactions.

```
src/
  contracts/            TransactionIn, TransactionCreated, AccountSummary, TransactionRecorded
  common/               config, observability, broker, client (CircuitBreaker + resilient_get)
  transactions_service/ POST /v1/transactions, GET /v1/transactions/{account_id}, publish event
  ledger_service/       consume idempotently, GET /v1/accounts/{account_id}/summary
  gateway/main.py       GET /bff/account/{id} resilient + degrade, POST /transactions -> 502 if down
tests/                  per-service, contract, end-to-end, observability, reconciliation, resilience, degradation
scripts/smoke.py        the end-to-end run, with a reconciliation check
```

**Money as integers.** Every amount is `amount_cents`, a positive integer of paise. A credit
adds to the balance and a debit subtracts. Rupees appear only in printed output, formatted from
the integer at the very end. There is no float anywhere in the money path, so there is no
rounding error to accumulate.

**The versioned contract.** The request, response, and event shapes live in one `contracts`
package, and the routes sit on a `/v1` path. A later change can add a field or a `/v2` without
breaking a caller on `/v1`, which is what makes the boundary safe to evolve.

**The resilient link.** The gateway calls the ledger through `resilient_get`: a timeout on every
call, a retry with backoff for a transient failure, and a `CircuitBreaker` that opens after a
run of failures and recovers after a cooldown. When the ledger is down, the dashboard returns a
null summary with a note, status 200. When the transactions service is down, a submit returns a
502. The correlation id is forwarded on the call, so one request spans both services in the logs.

**The reconciliation proof.** The key test records a mix of credits and debits and asserts the
ledger balance equals credits minus debits, in integer paise. That is the money domain's version
of a test: not that the code ran, but that the balance equals what the transactions say.

## The measured result

Running the smoke script end to end (a mixed run of five transactions for one account):

```text
ledger-service consumes the events and serves the account summary:
  /v1/accounts/acc-1/summary -> {'account_id': 'acc-1', 'count': 5, 'balance_cents': 8700}

reconciliation check (balance must equal credits minus debits, in paise):
  expected balance = 8700 (rupees 87.00)
  ledger balance   = 8700 (rupees 87.00)
  reconciled       = True

a duplicate event does not double-count (idempotent consumer):
  /v1/accounts/acc-1/summary -> {'account_id': 'acc-1', 'count': 5, 'balance_cents': 8700}

the gateway degrades cleanly when ledger-service is down:
  /bff/account/acc-1 -> 200 {'account_id': 'acc-1', 'summary': None, 'note': 'no data yet'}

unknown account escalates to a clear 404, not a guess:
  /v1/accounts/unknown/summary -> 404
```

The reconciliation line is one proof: the ledger balance of 8700 paise equals the credits minus
the debits. The degraded-gateway line is the other: with the ledger down, the request returns a
clear answer at status 200 rather than hanging. (A single failed call returns the note through
the transient-error path; once the breaker has opened after repeated failures, the note reads
that the service is temporarily unavailable. Both paths return a null summary at status 200, and
the breaker-open path is exercised directly in the resilience test.)

The full gate, from the `assignment02` folder:

```bash
poetry run pytest -q                     # 20 passed
poetry run ruff check src tests scripts  # All checks passed!
poetry run mypy src                       # Success: no issues found in 16 source files
```

## Why this is the right shape

Carrying money as integer paise removes a whole class of bug before it can start. A float balance
drifts, and in a money system a drift is an incident. Integers are exact, and the only place a
value becomes rupees is where a person reads it.

Versioning the contract is what lets the two services evolve without a coordinated release. A new
field is additive on `/v1`; a breaking change earns a `/v2` and a deprecation window. The
boundary is a promise, and versioning is how you keep it while still moving.

Wrapping the call is what keeps the gateway alive when the ledger is not. The timeout bounds the
wait, the retry hides a blip, the breaker leaves a dead dependency alone, and the fallback gives
the caller a clear answer. Together they turn one service's failure into a degraded feature
rather than a second outage.

## Going further (optional)

- Add a `/v2` of the summary that includes the last transaction time, and keep `/v1` working, to
  practise an additive contract change.
- Move the ledger to a background consumer so the summary updates continuously, and keep the
  reconciliation and idempotency guarantees.
- Add a per-account daily total and prove it reconciles against the transactions for the day.
