# Concurrency

*From chapter 22 ("Concurrency").*

Concurrency is a **decoupling strategy**: it separates *what* gets done from *when* it gets done. That decoupling can improve throughput and structure — but it makes the code dramatically harder to reason about.

## Why concurrency?

Two distinct reasons to adopt it:

1. **Structural.** A system decomposed into many small collaborating processes can be easier to reason about than one monolithic main loop.
2. **Performance.** Some workloads have strict throughput or response-time needs that single-threaded code cannot meet (aggregation across many I/O sources, per-user request handling, parallelizable analysis).

## Myths

- **"Concurrency always improves performance."** False. It helps only when there's enough wait time or independent work to amortize the coordination cost.
- **"Design doesn't change for concurrent code."** False. Concurrent design is fundamentally different.
- **"If the framework handles it (e.g., a web server), I don't need to understand concurrency."** False. You still need to understand concurrent update, deadlock, and starvation, or your code will silently corrupt data.

## Fundamental truths

- Concurrency incurs overhead in both performance and code volume.
- **Correct concurrency is complex, even for simple problems.**
- Concurrency bugs are usually non-reproducible, so they are often dismissed as "cosmic rays" — and thus never fixed.
- Adopting concurrency often requires a fundamental redesign.

Illustrative challenge: the trivial class `int get_next_id() { return ++last_id_used; }` has ~12,870 distinct bytecode execution paths when two threads call it on a shared instance. Some of those paths produce wrong results (two callers see the same ID). Changing `int` to `long` pushes that to ~2.7 million paths.

## Defense principles

### 1. SRP — separate concurrency from the rest of the code

Concurrency is its own reason to change, with its own lifecycle of development and tuning. Don't embed synchronization logic inside business logic. **Keep concurrency-related code separate.**

### 2. Limit the scope of shared data

Every critical section is a place you can forget to lock. More critical sections ⇒ more chances to miss one ⇒ higher probability of a silent corruption bug.

- Encapsulate aggressively.
- **Prefer immutable data** ("functional style") for concurrent modules.

### 3. Use copies of data

- Share nothing when possible.
- Give each thread a read-only copy; merge results at the end on a single thread.
- Allocation overhead is almost always cheaper than lock contention plus the cognitive overhead of correct locking.

### 4. Make threads as independent as possible

- Each thread handles one request with *all* its state local.
- Avoid shared mutable state as a design goal, not just as an optimization.

### 5. Know your language and library

- Use thread-safe collections (in Java: `java.util.concurrent.*`; in other ecosystems, the equivalent).
- Use framework-provided executors/pools rather than hand-rolled threads.
- Prefer nonblocking primitives where correct.
- Know which library APIs are thread-safe and which are not — assumptions here cause corruption.

## Execution models (learn these)

- **Producer / Consumer.** Queue mediates between producers and consumers; both wait on queue state.
- **Readers / Writers.** Many readers, occasional writers; strategy balances throughput against starvation.
- **Dining Philosophers.** Competing for shared resources; deadlock / livelock risk.

Most real-world concurrent problems are variations of these three. Practice them off-project so you have muscle memory when they show up in production.

## Keep concurrency out of business logic

- `synchronized` blocks / lock primitives inside domain methods make the code hard to read *and* hard to make correct.
- Push concurrency to the edge — a coordinator layer schedules work; the business logic stays single-threaded within each unit of work.

## Testing concurrent code

- Design tests that *expose* threading problems (run many iterations, vary thread counts, run on different hardware).
- Keep spurious failures — one-off test failures on concurrent code are usually real bugs. Do not silence them.

## GDScript / RTV notes

- **Godot is primarily single-threaded for scene-tree and script execution.** `_process`, `_physics_process`, `_input`, and most node callbacks run on the main thread in a defined order.
- **True threads** are available via `Thread`, `Semaphore`, `Mutex`, `WorkerThreadPool`. Used mainly for:
  - Loading assets off-thread.
  - Procedural generation.
  - Network I/O.
- **Never touch the scene tree from a non-main thread.** Scene-tree methods and property access are not thread-safe. Use `call_deferred()` to bounce a mutation back to the main thread.
- **`await`** is not concurrency in the threaded sense — it's cooperative suspension within the main thread. It *can* still create ordering bugs (state can change across an `await` boundary), but those are not data races.
- **Signal emission is synchronous by default.** If you need async dispatch, use `call_deferred` or connect with the `CONNECT_DEFERRED` flag.
- **In RTV modding**, concurrent code is rare. The likely place you'd hit it: background asset loading or heavy procedural work. When you do:
  - Isolate the thread's work; communicate via thread-safe channels (`WorkerThreadPool.add_task` is the idiomatic choice).
  - Never mutate game state from the worker; produce a result, hand it back via `call_deferred`, apply on main thread.
- **Do not sprinkle `Mutex` / `Semaphore` into gameplay scripts "for safety"** — you'll introduce deadlocks faster than you'll solve race conditions that aren't actually there.
