import sys, time, gc, platform


class PassengerNode:
    def __init__(self, pid, name, flight):
        self.id, self.name, self.flight, self.next = pid, name, flight, None

    def __str__(self): return f"[{self.id}] {self.name} - {self.flight}"


class CheckInQueue:
    def __init__(self):
        self.front = self.rear = None
        self.n = 0

    def enqueue(self, pid, name, flight):               # O(1)
        node = PassengerNode(pid, name, flight)
        if self.rear: self.rear.next = node
        else: self.front = node
        self.rear = node
        self.n += 1

    def dequeue(self):                                  # O(1)
        node = self.front
        if not node: return None
        self.front = node.next
        if not self.front: self.rear = None             # queue became empty
        node.next = None
        self.n -= 1
        return node

    def peek(self): return self.front

    def count(self): return self.n

    def display(self):
        c = self.front
        if not c: print("Queue is empty.")
        else: print("FRONT")
        while c: print("  ", c); c = c.next
        if self.front: print("REAR")


def ask(prompt, cast=str):
    while True:
        try: return cast(input(prompt).strip())
        except ValueError: print("Invalid input.")


def menu():
    q = CheckInQueue()
    while True:
        print("\n1.Add Passenger 2.Check-In 3.Peek Next 4.Display Queue 5.Count 6.Exit")
        ch = ask("> ", int)
        if ch == 1: q.enqueue(ask("ID: ", int), ask("Name: "), ask("Flight: ")); print("Passenger added.")
        elif ch == 2:
            p = q.dequeue(); print(f"{p.name} checked in successfully." if p else "Queue is empty.")
        elif ch == 3:
            p = q.peek(); print(f"Next: {p}" if p else "Queue is empty.")
        elif ch == 4: q.display()
        elif ch == 5: print("Passengers:", q.count())
        elif ch == 6: break


def test():
    q = CheckInQueue()
    for i, nm in enumerate(("Ali", "Leyla", "Nigar"), 1): q.enqueue(i, nm, "AZ101")
    assert q.peek().name == "Ali" and q.count() == 3
    assert [q.dequeue().name for _ in range(3)] == ["Ali", "Leyla", "Nigar"]      # FIFO
    assert q.dequeue() is None and q.front is None and q.rear is None
    q.enqueue(9, "Zed", "AZ1"); assert q.peek().name == "Zed" and q.count() == 1  # reuse after empty
    print("All Queue tests passed.")


def timed(setup, run, reps=3):
    r = []
    for _ in range(reps):
        s = setup(); gc.collect(); gc.disable()
        t = time.perf_counter(); run(s); r.append((time.perf_counter() - t) * 1000)
        gc.enable()
    return sorted(r)[reps // 2]


def bench():
    sizes, rows = [100, 1000, 10000], []
    print("System:", platform.platform(), "|", platform.processor(), "| Python", platform.python_version())
    print(f"{'N':>6} {'Enqueue(ms)':>12} {'Dequeue(ms)':>12} {'Peek(ms)':>12}   (total time for N operations)")
    for n in sizes:
        def filled():
            q = CheckInQueue()
            for i in range(n): q.enqueue(i, "p", "AZ101")
            return q
        enq = timed(CheckInQueue, lambda q: [q.enqueue(i, "p", "AZ101") for i in range(n)])
        deq = timed(filled, lambda q: [q.dequeue() for _ in range(n)])
        pk = timed(filled, lambda q: [q.peek() for _ in range(n)])
        rows.append((enq, deq, pk))
        print(f"{n:>6} {enq:>12.3f} {deq:>12.3f} {pk:>12.3f}")
    try:
        import matplotlib.pyplot as plt
        for k, lab in enumerate(("Enqueue", "Dequeue", "Peek")):
            plt.plot(sizes, [r[k] for r in rows], marker="o", label=lab)
        plt.xlabel("Element count"); plt.ylabel("Time (ms)"); plt.legend(); plt.grid(alpha=.3)
        plt.title("Task 3 - Queue"); plt.savefig("task3_graph.png", dpi=150)
        print("Graph saved: task3_graph.png")
    except ImportError:
        print("pip install matplotlib to get the graph")
    return sizes, rows


if __name__ == "__main__":
    {"test": test, "bench": bench}.get(sys.argv[1] if len(sys.argv) > 1 else "", menu)()
