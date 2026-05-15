import threading


class JobScheduler:
    """Base class — do not modify."""

    def submit(self, name: str) -> int:
        raise NotImplementedError

    def get_job(self, job_id: int):
        return None

    def cancel(self, job_id: int) -> bool:
        return False

    def start_next(self):
        return None

    def finish(self, job_id: int) -> bool:
        return False

    def get_counts(self) -> dict:
        return {"queued": 0, "running": 0, "done": 0, "cancelled": 0}

    def run_parallel(self, n: int):
        pass


class JobSchedulerImpl(JobScheduler):

    def __init__(self):
        self.jobs = {}
        self.next_id = 1
        self.lock = threading.Lock()


    # --- Level 1 ---

    def submit(self, name: str) -> int:
        job_id=self.next_id
        self.jobs[job_id] = {"id": job_id, "name": name, "status": "queued"}
        self.next_id += 1
        return job_id

    def get_job(self, job_id: int):
        return self.jobs.get(job_id)

    def cancel(self, job_id: int) -> bool:
        if job_id in self.jobs:
            if self.jobs[job_id]["status"] == "queued":
                self.jobs[job_id]["status"] = "cancelled"
                return True
            else:
                return False
        else:
            return False    

    # --- Level 2 ---

    def start_next(self):
        queued_jobs = [x for x in self.jobs.values() if x["status"] == "queued"]
        if len(queued_jobs) > 0:
            sorted_queue = sorted(queued_jobs, key=lambda x: x["id"])
            next_job = sorted_queue[0]
            next_job["status"] = "running"
            return next_job
        else:
            return None


    def finish(self, job_id: int) -> bool:
        if job_id in self.jobs and self.jobs[job_id]["status"]=="running":
            self.jobs[job_id]["status"] = "done"
            return True
        return False

    def get_counts(self) -> dict:
        counts = {"queued": 0, "running": 0, "done": 0, "cancelled": 0}
        for job in self.jobs.values():
            counts[job["status"]] += 1
        return counts

    # --- Level 3 ---

    def run_parallel(self, n: int):

        def worker():
            while True:
                with self.lock:
                    job = self.start_next()
                if job is None:
                    break
                self.finish(job["id"])

        threads = []
        for _ in range(n):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
                

