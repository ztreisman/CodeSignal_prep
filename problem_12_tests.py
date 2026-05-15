"""
Problem 12 — Job Scheduler
==========================

Implement a JobSchedulerImpl class in job_scheduler_impl.py.

SPEC
----

Level 1: Submit and cancel jobs.

  submit(name: str) -> int
    Submit a new job. Status starts as "queued".
    Return the job_id (auto-assigned, starting at 1).

  get_job(job_id: int) -> dict | None
    Return {"id": int, "name": str, "status": str} or None if not found.

  cancel(job_id: int) -> bool
    Cancel the job if its status is "queued".
    Return True if cancelled, False if not found or not queued.

Level 2: Start and finish jobs.

  start_next() -> dict | None
    Find the queued job with the lowest id, mark it "running", return it.
    Return None if no queued jobs exist.

  finish(job_id: int) -> bool
    Mark a "running" job as "done".
    Return True if found and was running, False otherwise.

  get_counts() -> dict
    Return {"queued": int, "running": int, "done": int, "cancelled": int}.

Level 3: Parallel workers.

  run_parallel(n: int)
    Spawn n worker threads. Each worker loops:
      1. Call start_next(). If None, stop.
      2. Call finish() on that job.
    All workers run simultaneously until there are no queued jobs left.
    Must be thread-safe: two workers must never receive the same job.

Run tests:
  python -m unittest problem_12_tests.py
  python -m unittest problem_12_tests.Level1
"""

import unittest
from job_scheduler_impl import JobSchedulerImpl


class Level1(unittest.TestCase):

    def setUp(self):
        self.js = JobSchedulerImpl()

    def test_submit_returns_sequential_ids(self):
        self.assertEqual(self.js.submit("job1"), 1)
        self.assertEqual(self.js.submit("job2"), 2)
        self.assertEqual(self.js.submit("job3"), 3)

    def test_get_job_fields(self):
        self.js.submit("build")
        job = self.js.get_job(1)
        self.assertEqual(job["id"], 1)
        self.assertEqual(job["name"], "build")
        self.assertEqual(job["status"], "queued")

    def test_get_job_not_found(self):
        self.assertIsNone(self.js.get_job(99))

    def test_cancel_queued_job(self):
        self.js.submit("job1")
        self.assertTrue(self.js.cancel(1))
        self.assertEqual(self.js.get_job(1)["status"], "cancelled")

    def test_cancel_not_found(self):
        self.assertFalse(self.js.cancel(99))

    def test_cancel_already_cancelled(self):
        self.js.submit("job1")
        self.js.cancel(1)
        self.assertFalse(self.js.cancel(1))


class Level2(unittest.TestCase):

    def setUp(self):
        self.js = JobSchedulerImpl()
        self.js.submit("job1")   # id 1
        self.js.submit("job2")   # id 2
        self.js.submit("job3")   # id 3

    def test_start_next_returns_lowest_id(self):
        job = self.js.start_next()
        self.assertEqual(job["id"], 1)
        self.assertEqual(job["status"], "running")

    def test_start_next_skips_cancelled(self):
        self.js.cancel(1)
        job = self.js.start_next()
        self.assertEqual(job["id"], 2)

    def test_start_next_no_queued(self):
        self.js.cancel(1)
        self.js.cancel(2)
        self.js.cancel(3)
        self.assertIsNone(self.js.start_next())

    def test_start_next_sequential(self):
        self.assertEqual(self.js.start_next()["id"], 1)
        self.assertEqual(self.js.start_next()["id"], 2)
        self.assertEqual(self.js.start_next()["id"], 3)
        self.assertIsNone(self.js.start_next())

    def test_finish_running_job(self):
        self.js.start_next()
        self.assertTrue(self.js.finish(1))
        self.assertEqual(self.js.get_job(1)["status"], "done")

    def test_finish_queued_job_fails(self):
        self.assertFalse(self.js.finish(1))

    def test_finish_not_found(self):
        self.assertFalse(self.js.finish(99))

    def test_get_counts(self):
        self.js.cancel(1)
        self.js.start_next()   # starts job 2
        counts = self.js.get_counts()
        self.assertEqual(counts["queued"], 1)
        self.assertEqual(counts["running"], 1)
        self.assertEqual(counts["done"], 0)
        self.assertEqual(counts["cancelled"], 1)

    def test_get_counts_after_finish(self):
        self.js.start_next()
        self.js.finish(1)
        counts = self.js.get_counts()
        self.assertEqual(counts["done"], 1)
        self.assertEqual(counts["running"], 0)


class Level3(unittest.TestCase):

    def setUp(self):
        self.js = JobSchedulerImpl()

    def test_run_parallel_completes_all(self):
        for i in range(10):
            self.js.submit(f"job{i}")
        self.js.run_parallel(3)
        counts = self.js.get_counts()
        self.assertEqual(counts["done"], 10)
        self.assertEqual(counts["queued"], 0)
        self.assertEqual(counts["running"], 0)

    def test_run_parallel_no_double_processing(self):
        for i in range(20):
            self.js.submit(f"job{i}")
        self.js.run_parallel(5)
        for i in range(1, 21):
            self.assertEqual(self.js.get_job(i)["status"], "done")

    def test_run_parallel_skips_cancelled(self):
        for i in range(10):
            self.js.submit(f"job{i}")
        for i in range(1, 6):
            self.js.cancel(i)
        self.js.run_parallel(2)
        counts = self.js.get_counts()
        self.assertEqual(counts["done"], 5)
        self.assertEqual(counts["cancelled"], 5)
        self.assertEqual(counts["queued"], 0)

    def test_run_parallel_single_worker(self):
        for i in range(5):
            self.js.submit(f"job{i}")
        self.js.run_parallel(1)
        self.assertEqual(self.js.get_counts()["done"], 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
