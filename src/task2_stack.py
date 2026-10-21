import sys, time, gc, platform
from datetime import datetime


class PageNode:
    def __init__(self, pid, url):
        self.id, self.url, self.next = pid, url, None
        self.time = datetime.now().strftime("%H:%M:%S")

    def __str__(self): return f"[{self.id}] {self.url} (visited {self.time})"


class BrowserHistory:
    def __init__(self):
        self.top, self.n, self.next_id = None, 0, 1

    def push(self, url):                                # O(1)
        node = PageNode(self.next_id, url)
        node.next, self.top = self.top, node
        self.next_id += 1; self.n += 1
        return node

    def pop(self):                                      # O(1)
        node = self.top
        if node: self.top, node.next = node.next, None; self.n -= 1
        return node

    def back(self):                                     # leave current page, return previous
        if self.n <= 1: return None
        self.pop()
        return self.top

    def current(self): return self.top

    def display(self):
        c = self.top
        if not c: print("History is empty.")
        else: print("TOP")
        while c: print("  ", c); c = c.next


def ask(prompt, cast=str):
    while True:
        try: return cast(input(prompt).strip())
        except ValueError: print("Invalid input.")


def menu():
    h = BrowserHistory()
    while True:
        print("\n1.Visit Page 2.Back 3.Current Page 4.Display History 5.Exit")
        ch = ask("> ", int)
        if ch == 1: print("Visited:", h.push(ask("URL: ")))
        elif ch == 2:
            p = h.back(); print(f"Back to: {p}" if p else "Cannot go back.")
        elif ch == 3:
            p = h.current(); print(f"Current: {p}" if p else "No page open.")
        elif ch == 4: h.display()
        elif ch == 5: break


def test():
    h = BrowserHistory()
    for u in ("a", "b", "c"): h.push(u)
    assert h.current().url == "c" and h.n == 3
    assert h.back().url == "b" and h.back().url == "a" and h.back() is None and h.n == 1   # LIFO
    assert h.pop().url == "a" and h.pop() is None and h.n == 0
    print("All Stack tests passed.")


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
    print(f"{'N':>6} {'Push(ms)':>12} {'Pop(ms)':>12}   (total time for N operations)")
    for n in sizes:
        def filled():
            h = BrowserHistory()
            for i in range(n): h.push("u")
            return h
        push = timed(BrowserHistory, lambda h: [h.push("u") for _ in range(n)])
        pop = timed(filled, lambda h: [h.pop() for _ in range(n)])
        rows.append((push, pop))
        print(f"{n:>6} {push:>12.3f} {pop:>12.3f}")
    try:
        import matplotlib.pyplot as plt
        for k, lab in enumerate(("Push", "Pop")):
            plt.plot(sizes, [r[k] for r in rows], marker="o", label=lab)
        plt.xlabel("Operation count"); plt.ylabel("Time (ms)"); plt.legend(); plt.grid(alpha=.3)
        plt.title("Task 2 - Stack"); plt.savefig("task2_graph.png", dpi=150)
        print("Graph saved: task2_graph.png")
    except ImportError:
        print("pip install matplotlib to get the graph")
    return sizes, rows


if __name__ == "__main__":
    {"test": test, "bench": bench}.get(sys.argv[1] if len(sys.argv) > 1 else "", menu)()
