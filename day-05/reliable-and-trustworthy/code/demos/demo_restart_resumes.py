"""Resume from a checkpoint after a crash (reliability): restart where you stopped.

The concept, in plain words:
    A batch job processes many records. If it crashes halfway and restarts from the
    beginning, it redoes work and can duplicate side effects. If it restarts but skips
    the done part, it can lose records. The fix is a checkpoint: after each record, save
    the index of the last one finished. On restart, read the checkpoint and continue
    from the next record. Pair that with idempotent writes (writing the same record
    twice is the same as once) and a crash costs you nothing but a little repeated
    effort.

Why a fresher should care:
    Long jobs will be interrupted: a deploy, a node reboot, an out-of-memory kill. A
    checkpoint turns an interruption into a pause instead of a corruption, with no lost
    or duplicated records.

What this demo shows:
    We process 10 records, saving a checkpoint after each. We "crash" after record 4,
    then restart. The restart reads the checkpoint and finishes records 5 to 10. The
    final store holds each record exactly once: none lost, none duplicated.

Run:  poetry run python demo_restart_resumes.py
"""

from __future__ import annotations

RECORDS = [f"R-{i:02d}" for i in range(1, 11)]  # the batch: R-01 through R-10


class Job:
    """A resumable batch job: a checkpoint index plus an idempotent set-backed store."""

    def __init__(self) -> None:
        self.checkpoint = 0  # count of records confirmed done (0 means nothing yet)
        self.store: dict[str, str] = {}  # keyed by id: a repeat write is a no-op

    def process_until(self, stop_before: int | None = None) -> None:
        """Process records after the checkpoint, optionally crashing before an index.

        stop_before models a crash: when we reach that index we stop without
        advancing further, as if the process died mid-run. The checkpoint only
        moves after a record is safely written.
        """
        for index in range(self.checkpoint, len(RECORDS)):
            if stop_before is not None and index == stop_before:
                print(f"  crash before record index {index} ({RECORDS[index]})")
                return
            record_id = RECORDS[index]
            self.store[record_id] = f"processed:{record_id}"  # idempotent write
            self.checkpoint = index + 1  # advance only after the write lands


def main() -> None:
    job = Job()

    # First run: process records, then crash after finishing index 3 (record R-04).
    print("first run:")
    job.process_until(stop_before=4)
    done_through = RECORDS[job.checkpoint - 1]
    print(f"  checkpoint after crash: {job.checkpoint} (done through {done_through})")

    # Restart: the same job reads its checkpoint and continues, nothing replayed
    # from the start.
    print("restart:")
    job.process_until()
    print(f"  checkpoint after finish: {job.checkpoint}")

    processed = sorted(job.store)
    print(f"\nfinal store holds {len(processed)} records: {processed}")
    no_lost = processed == RECORDS
    no_dupes = len(job.store) == len(RECORDS)
    print(f"no lost records: {no_lost}; no duplicated records: {no_dupes}")


if __name__ == "__main__":
    main()
