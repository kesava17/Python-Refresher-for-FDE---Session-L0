# Microservices demos

Six tiny, runnable demos, one idea each, standard library only. They are the "see it" to the
live lab's "build it": each isolates a single microservice concept with no framework and no
network beyond a local port, so the idea is visible on its own.

```bash
poetry install
poetry run python demo_two_services.py
```

| Demo | The idea | You should see |
| --- | --- | --- |
| `demo_two_services.py` | a call between services crosses the network as HTTP | an orders service calling an inventory service over a local port |
| `demo_sync_vs_async.py` | wait for the answer, or hand the work off | a blocking call taking 0.20s, and a handoff returning at once |
| `demo_timeout_retry.py` | a timeout and a retry with backoff | two failures retried to success, and a slow call cut off at 0.3s |
| `demo_circuit_breaker.py` | stop calling a failing dependency, then recover | the circuit opening on the third failure and half-opening after cooldown |
| `demo_idempotent_consumer.py` | at-least-once means duplicates; be idempotent | a redelivered event skipped, so the total does not double-count |
| `demo_data_per_service.py` | each service owns its store; state moves by event | the query side building its own view without opening the ingest store |

See `cookbook.md` for the guided walkthrough of all six, with what to run, what to watch for,
and what to change. Everything runs offline with `python <name>.py` too; the demos need only
the standard library.
