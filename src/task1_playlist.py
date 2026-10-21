import sys, time, random, gc, platform


class SongNode:
    def __init__(self, sid, name, artist, dur=0):
        self.id, self.name, self.artist, self.dur, self.next = sid, name, artist, dur, None

    def __str__(self):
        return f"[{self.id}] {self.name} - {self.artist} ({self.dur // 60}:{self.dur % 60:02d})"


class Playlist:
    def __init__(self):
        self.head = self.tail = self.cur = None
        self.n = 0

    def add(self, sid, name, artist, dur=0):            # O(1) thanks to tail
        node = SongNode(sid, name, artist, dur)
        if self.tail: self.tail.next = node
        else: self.head = node
        self.tail = node
        self.n += 1

    def search(self, sid):                              # O(n)
        c = self.head
        while c and c.id != sid: c = c.next
        return c

    def delete(self, sid):                              # O(n)
        prev, c = None, self.head
        while c and c.id != sid: prev, c = c, c.next
        if not c: return False
        if prev: prev.next = c.next
        else: self.head = c.next
        if c is self.tail: self.tail = prev
        if c is self.cur: self.cur = c.next
        self.n -= 1
        return True

    def display(self):
        c, i = self.head, 1
        if not c: print("Playlist is empty.")
        while c: print(f"{i}. {c}"); c, i = c.next, i + 1

    def count(self): return self.n

    def play_next(self):                                # O(1), wraps to start
        if not self.head: return None
        song = self.cur or self.head
        self.cur = song.next
        return song


def ask(prompt, cast=str):
    while True:
        try: return cast(input(prompt).strip())
        except ValueError: print("Invalid input.")


def menu():
    pl = Playlist()
    while True:
        print("\n1.Add Song 2.Delete Song 3.Search Song 4.Display 5.Play Next 6.Count 7.Exit")
        ch = ask("> ", int)
        if ch == 1:
            sid = ask("ID: ", int)
            if pl.search(sid): print("ID already exists."); continue
            pl.add(sid, ask("Name: "), ask("Artist: "), ask("Duration (sec): ", int))
            print("Song added successfully.")
        elif ch == 2: print("Deleted." if pl.delete(ask("ID: ", int)) else "Not found.")
        elif ch == 3:
            s = pl.search(ask("ID: ", int)); print(s if s else "Not found.")
        elif ch == 4: pl.display()
        elif ch == 5:
            s = pl.play_next(); print(f"Now playing: {s}" if s else "Playlist is empty.")
        elif ch == 6: print("Songs:", pl.count())
        elif ch == 7: break


def test():
    p = Playlist()
    for i in (1, 2, 3): p.add(i, f"S{i}", "A", 60)
    assert p.count() == 3 and p.search(2).name == "S2" and p.search(9) is None
    assert [p.play_next().id for _ in range(4)] == [1, 2, 3, 1]       # wraps
    assert p.delete(1) and p.delete(3) and not p.delete(3)            # head, tail
    p.add(4, "S4", "A"); assert p.tail.id == 4 and p.count() == 2     # tail stays valid
    assert p.delete(2) and p.delete(4) and p.head is None and p.tail is None
    print("All Playlist tests passed.")


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
    print(f"{'N':>6} {'Insert(ms)':>12} {'Search(ms)':>12} {'Delete(ms)':>12}   (total time for N operations)")
    for n in sizes:
        ids = list(range(n)); random.Random(42).shuffle(ids)
        def filled():
            p = Playlist()
            for i in range(n): p.add(i, "s", "a")
            return p
        ins = timed(Playlist, lambda p: [p.add(i, "s", "a") for i in range(n)])
        sea = timed(filled, lambda p: [p.search(i) for i in ids])
        dele = timed(filled, lambda p: [p.delete(i) for i in ids])
        rows.append((ins, sea, dele))
        print(f"{n:>6} {ins:>12.3f} {sea:>12.3f} {dele:>12.3f}")
    try:
        import matplotlib.pyplot as plt
        for k, lab in enumerate(("Insert", "Search", "Delete")):
            plt.plot(sizes, [r[k] for r in rows], marker="o", label=lab)
        plt.xlabel("Element count"); plt.ylabel("Time (ms)"); plt.legend(); plt.grid(alpha=.3)
        plt.title("Task 1 - Linked List"); plt.savefig("task1_graph.png", dpi=150)
        print("Graph saved: task1_graph.png")
    except ImportError:
        print("pip install matplotlib to get the graph")
    return sizes, rows


if __name__ == "__main__":
    {"test": test, "bench": bench}.get(sys.argv[1] if len(sys.argv) > 1 else "", menu)()
