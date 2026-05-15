# Problem 1

def summarize(nums, label="data"):
	count = len(nums)
	tot = 0
	for i in range(count):
		tot += nums[i]
	mean = tot / count
	rang = max(nums)-min(nums)

	return {"label": label, "count":count, "mean":mean, "range":rang}


# Problem 2a

def summarize(nums, label="data"):
	count = len(nums)
	tot = sum(nums)
	mean = tot / count
	rang = max(nums)-min(nums)

	return {"label": label, "count":count, "mean":mean, "range":rang}


# Problem 3

def word_counts(text):
	words = text.split()
	return {x:len([y for y in words if y==x]) for x in words}

# better solution

def word_counts(text):
    words = text.split()
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts

# Problem 4

class BankAccount:
	def __init__(self, owner, balance=0):
		self.owner = owner
		self.balance = balance
	
	def deposit(self, amount):
		self.balance += amount

	def withdraw(self, amount):
		if self.balance < amount:
			raise ValueError("Insufficient Funds")
		self.balance -= amount
			
	
	def __str__(self):
		return f"Account[{self.owner}]: ${self.balance:.2f}"

# Problem 5

def safe_divide(a,b):
	if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
		raise TypeError("Arguments must be numeric")
	if b == 0:
		raise ValueError("Cannot divide by zero")
	return a/b

def try_divide(a,b):
	try:
		return safe_divide(a,b)
	except Exception:
		return None

# Problem 6 

class TaskManager:
	
	def __init__(self):
		self.tasks = {}
		self.next_id = 1
		
	def add_task(self, title):
		self.tasks[self.next_id] = {"id":self.next_id, "title":title, "status":"pending"}
		self.next_id += 1
		return self.next_id - 1

	def start_task(self, id):
		if id not in self.tasks:
			raise ValueError("Task not found")
		if self.tasks[id]["status"] != "pending":
			raise ValueError(f"Task not pending, task is {self.tasks[id]['status']}.")
		self.tasks[id]["status"] = "in_progress"

	def complete_task(self, id):
		if id not in self.tasks:
			raise ValueError("Task not found")
		if self.tasks[id]["status"] != "in_progress":
			raise ValueError(f"Task not in_progress, task is {self.tasks[id]['status']}.")
		self.tasks[id]["status"] ="done"

	def get_tasks(self, status=None):
		tasks = list(self.tasks.values())
		if status is not None:
			tasks = [t for t in tasks if t["status"]==status]
		return tasks
		
# Problem 7

def analyze_scores(records):
	
	records = sorted(records, key=lambda x:x["score"], reverse=True)
	top3 = [x['name'] for x in records[:3]]
	
	scores = [x['score'] for x in records]
	average = round(sum(scores)/len(scores),2)
	
	counts = {}
	for x in scores:
		counts[x] = counts.get(x, 0) + 1
	counts = sorted(counts.items(), key=lambda item:(-item[1], item[0]))
	most_common_score = counts[0][0]
	
	return {"top3":top3, "average":average, "most_common_score":most_common_score}

# Problem 8

import threading

def run_parallel(funcs):
	
	threads = []
	for f in funcs:
		t = threading.Thread(target=f)
		t.start()
		threads.append(t)
	for t in threads:
		t.join()

# Problem 9

import threading

class ThreadSafeCounter:

	def __init__(self, count=0):
		self.lock = threading.Lock()
		self._count = count

	def increment(self):
		with self.lock:
			self._count +=1

	@property
	def count(self):
		with self.lock:
			return self._count
		
	
	
def stress_test():
	
	tsc = ThreadSafeCounter()
	threads = []

	def wrapper():
		for _ in range(100):
			tsc.increment()

	for _ in range(100):
		t = threading.Thread(target=wrapper)
		t.start()
		threads.append(t)

	
	for t in threads:
		t.join()
	
	return tsc.count
	
# Problem 10

import asyncio

async def run_async(coros):
	await asyncio.gather(*coros)


