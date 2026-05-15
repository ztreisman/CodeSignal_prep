# Python Coding Assessment Prep — Tutoring Template & Study Materials

This repository serves two purposes:

1. **Complete study materials** from a focused Python tutoring session for a
   CodeSignal-style coding assessment (Anthropic Fellows Program, May 2026)
2. **A reusable template** for anyone who wants to recreate this tutoring
   experience using Claude or another capable LLM

---

## Recreating the Tutoring Experience

To use this as a tutoring template:

1. Start a new conversation with Claude (claude.ai or Claude Code)
2. Paste the contents of [`tutor_context.md`](tutor_context.md) at the start
3. Describe your background: programming experience, timeline, what you know
4. Ask Claude to begin the curriculum

The tutor will give you problems before explanations, give direct feedback on
errors, and simulate the CodeSignal environment with spec + test suite problems.

The [`python_idioms.pdf`](python_idioms.pdf) reference sheet was built
incrementally throughout the session and is useful during practice. **It is a
study tool only** — during a proctored assessment, only official language
documentation (docs.python.org) is allowed. The Quick Reference section at the
top of the PDF lists the exact doc URLs to open at the start of the assessment.

---

## Study Materials

### Reference
| File | Description |
|------|-------------|
| [`python_idioms.pdf`](python_idioms.pdf) | Reference sheet: idioms, patterns, doc links — **study tool only**, not for use during proctored assessments |
| [`python_idioms.tex`](python_idioms.tex) | LaTeX source for the reference sheet |
| [`journal.md`](journal.md) | Session journal: what was covered, bugs hit, weak spots, assessment strategy |
| [`tutor_context.md`](tutor_context.md) | Tutor context file — use this to recreate the session |

### Fundamentals (Problems 1–10)
| File | Description |
|------|-------------|
| [`python_bootcamp.py`](python_bootcamp.py) | Problems 1–10: functions, lists, dicts, classes, error handling, threading, asyncio |
| [`drills.py`](drills.py) | Focused drills: string parsing, string formatting, `any()`/`all()`, `queue.Queue` worker pool |
| [`gather_results.py`](gather_results.py) | Threading drill: parallel map with ordered results and `nonlocal` |

### Full System Problems (CodeSignal-style, timed)
Each problem has an implementation file and a test suite with the spec in the docstring.

| Problem | Files | Key patterns |
|---------|-------|--------------|
| Message Board | [`message_board_impl.py`](message_board_impl.py), [`problem_11_tests.py`](problem_11_tests.py) | likes, ranking, parallel action processing |
| Job Scheduler | [`job_scheduler_impl.py`](job_scheduler_impl.py), [`problem_12_tests.py`](problem_12_tests.py) | worker threads competing for jobs |
| Library System (mock 1) | [`library_impl.py`](library_impl.py), [`mock_tests.py`](mock_tests.py) | checkout/return, stats, concurrent batch |
| Tournament (mock 2) | [`tournament_impl.py`](tournament_impl.py), [`tournament_tests.py`](tournament_tests.py) | rankings, stats, parallel recording |
| KV Store (mock 3) | [`kvstore_impl.py`](kvstore_impl.py), [`kvstore_tests.py`](kvstore_tests.py) | TTL, transactions, concurrent batch |

### Running tests
```bash
# Run all tests for a problem
python -m unittest problem_11_tests.py

# Run one level at a time
python -m unittest problem_11_tests.Level1

# Run all mocks
python -m unittest mock_tests.py
python -m unittest tournament_tests.py
python -m unittest kvstore_tests.py
```

---

## Curriculum Overview

The full curriculum is described in [`tutor_context.md`](tutor_context.md).
At a high level:

- **Phase 1** — Python fundamentals for programmers from other languages
- **Phase 2** — CodeSignal-style patterns (manager classes, sorting, filtering)
- **Phase 3** — Concurrency (`threading`, `asyncio`, `queue.Queue`)
- **Phase 4** — Advanced patterns (TTL, transactions, LRU cache)

The session in this repo covered Phases 1–3 fully and Phase 4 partially in
approximately 3 days of practice.

---

## Key Patterns Quick Reference

```python
# Dict counter
counts[key] = counts.get(key, 0) + 1

# Sort descending by score, ascending by name on tie
sorted(items, key=lambda x: (-x["score"], x["name"]))

# Manager class skeleton
class SystemImpl:
    def __init__(self):
        self.items = {}            # id -> item dict (O(1) lookup)
        self.next_id = 1
        self.lock = threading.Lock()

# Thread-safe worker pool
def worker():
    while True:
        with self.lock:
            item = self.get_next()   # grab and mark atomically
        if item is None:
            break
        process(item)               # work outside lock

# TTL pattern
self.expires[key] = time.time() + ttl      # on set_with_ttl
expired = time.time() >= self.expires[key]  # on read

# Transaction pattern
_DELETED = object()   # sentinel for buffered deletions
self.buffer = None    # None = no transaction; dict = open transaction
```
