#Implement gather_results(tasks, n_workers):
#  - tasks: a list of zero-argument functions, each returning a value
#  - n_workers: number of worker threads
#  - Run all tasks in parallel using a worker pool
#  - Return a list of return values in the same order as tasks

#Example:
#  import time
#  tasks = [lambda: 1, lambda: 2, lambda: 3]
#  gather_results(tasks, 2)  →  [1, 2, 3]

import threading

def gather_results(tasks, n_workers):
  lock = threading.Lock() 
  current_task = 0
  results = [None]*len(tasks)
  
  def worker():
     nonlocal current_task
     while True:
        with lock:
          if current_task >= len(tasks):
            break
          i = current_task
          current_task += 1
        results[i]=tasks[i]()
  
  threads = []

  for _ in range(n_workers):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)
  
  for t in threads:
    t.join()
  
  return results


if __name__ == "__main__":
    # basic correctness
    tasks = [lambda i=i: i * 2 for i in range(6)]
    print(gather_results(tasks, 3))   # expect [0, 2, 4, 6, 8, 10]

    # more workers than tasks
    tasks = [lambda: 99]
    print(gather_results(tasks, 5))   # expect [99]

    # actual parallelism
    import time
    tasks = [lambda: time.sleep(0.1) or 1 for _ in range(4)]
    start = time.time()
    gather_results(tasks, 4)
    print(f"elapsed: {time.time()-start:.2f}s")   # expect ~0.1s, not ~0.4s
