## Module-Level Ordering

### The Rule

Within a Python module, elements appear in this order from top to bottom:

1. **Imports**
2. **Module-level constants** (ALL_CAPS)
3. **Public classes** (dataclasses, Pydantic models, enums)
4. **Public functions** (the API surface)
5. **Private classes** (prefixed with `_`)
6. **Private constants / data** (prefixed with `_`, e.g. `_LOOKUP_TABLE = {...}`)
7. **Private functions** (prefixed with `_`)


**Why constants before functions?** Constants define the vocabulary of the module. A reader encountering `_CLASSIFICATION_SPECS[key]` inside a function can scroll up to find it, not down. Constants are reference material; functions are behavior.

**Why classes before functions?** Classes define the data shapes that functions produce and consume. Seeing `JiraTicketAction` before `build_jira_ticket_action()` tells the reader what the function returns before they read how.

### Exception: Factory Pattern

When a module uses the **factory pattern** (ABC + factory function + implementation classes), the factory function should come right after the ABC, **before** the implementation classes:

```
ABC/Interface class
Factory function          ← public function between classes (allowed here)
Implementation class A
Implementation class B
Private helpers
```

**Why?** The factory function IS the public API — external callers use `create_foo()` and the `Foo` ABC, never instantiating implementations directly. Placing the factory after all implementations would force readers to scroll past internal details to find the one function they actually call. The factory serves as a table of contents: "here's the interface, here's how to get one, and if you care, here's how each backend works."

This exception applies only when:
- There's an ABC/interface that defines the contract
- A factory function creates the implementations
- External callers only use the factory + ABC, never instantiate implementations directly

## Function/Method Ordering Within a File

### The Rule

**Public first, private last — no exceptions.**

When placing functions or methods in a class or module, always follow this order:

1. **Public methods / functions** (the API surface) — at the top
2. **Private / helper methods** (prefixed with `_`) — below the public ones

### Verify Visibility Before Ordering

A function without `_` prefix is NOT necessarily public. If a non-underscore function is called by another function **in the same file**, check whether it also has external callers. If not, it's an internal helper masquerading as public — rename to `_private` and move to the private section.

**Quick check**: scan the file for `def foo(` without `_`. For each, search the same file for calls to `foo(`. If found, grep externally to confirm no imports exist. If no external imports → rename to `_foo`.

This applies even when private methods are heavily reused by many public methods. The rationale: public methods are the first level readers care about, and readability is better when they appear first. Private method details are rarely needed as long as they are properly named.


### Top-Down Reading Order Within Public Functions

When public functions call each other, place **callers before callees** — the higher-level function appears first, the lower-level building block it delegates to appears after. This follows the "newspaper style" from Clean Code: you read from the headline (high-level intent) down to the details (implementation).

```python
# CORRECT: caller before callee
def fetch_story_subtasks(url, email, token, story_key):
    jql = f'parent = "{story_key}" AND issuetype = Subtask'
    return search_tickets(url, email, token, jql)


def search_tickets(url, email, token, jql, limit=100): ...
```

```python
# WRONG: callee before caller
def search_tickets(url, email, token, jql, limit=100): ...


def fetch_story_subtasks(url, email, token, story_key):
    jql = f'parent = "{story_key}" AND issuetype = Subtask'
    return search_tickets(url, email, token, jql)
```

Functions that don't call each other (standalone at the same level) can appear in any order among themselves.

### BDD / Integration Test Step Definitions

For BDD-style test files (e.g. pytest-bdd step definitions), keep the **natural reading order**:

1. `@given` steps — first
2. `@when` steps — middle
3. `@then` steps — last


### Quick Reference

| Context | Order |
|---------|-------|
| Class methods | Public on top, `_private` below |
| Module-level functions | Public on top, `_private` below |
| BDD step definitions | `@given` → `@when` → `@then` |

---

## Decision: Local Function vs Class/Module Level

### The Rule

**Default to class/module-level private methods.** Local functions are allowed only when they don't break reading flow.

The core principle: **never interleave low-level function definitions with high-level business logic.** Readers should be able to follow the main flow without being forced to context-switch into implementation details mid-method.



### Decision Flow

```
Is this function used by more than one caller?
  ├─ YES → Class/module level method (no question)
  └─ NO → Does defining it locally break the reading flow of the parent?
           ├─ YES (interleaved with business logic) → Class/module level method
           └─ NO (can be batched at top, before main flow) → Local function is acceptable
```

### Placement Options

| Option | When to Use | How |
|--------|-------------|-----|
| **A) Class/module-level method** | Default. Always safe. Required if reused or if local placement would interrupt flow. | Private method below public methods. Use `functools.partial` if the caller needs to bind extra state. |
| **B) Local, batched at top** | Use very sparingly. Only if single-caller AND definitions can be grouped before the main flow starts. | All local defs together at the function start, then uninterrupted main logic below. |

### Example: BAD — Local functions interleaved with business logic

```python
# BAD: definitions scattered between business logic lines
def process_order(order):
    items = validate_order(order)

    def calculate_discount(item):  # <-- interrupts the flow
        return item.price * 0.1 if item.quantity > 10 else 0

    discounted = [apply(calculate_discount, i) for i in items]

    def format_receipt(item, discount):  # <-- interrupts again
        return f"{item.name}: {item.price - discount}"

    return [format_receipt(i, d) for i, d in zip(items, discounted)]
```

### Example: OK — Local functions batched at top

```python
# OK: all definitions first, then uninterrupted flow
def process_order(order):
    def calculate_discount(item):
        return item.price * 0.1 if item.quantity > 10 else 0

    def format_receipt(item, discount):
        return f"{item.name}: {item.price - discount}"

    # --- main flow (uninterrupted) ---
    items = validate_order(order)
    discounted = [calculate_discount(i) for i in items]
    return [format_receipt(i, d) for i, d in zip(items, discounted)]
```

### Example: PREFERRED — Class-level methods (default)

```python
# PREFERRED: clean separation, main flow reads like a summary
class OrderProcessor:
    def process_order(self, order):
        items = self._validate(order)
        discounted = [self._calculate_discount(i) for i in items]
        return [self._format_receipt(i, d) for i, d in zip(items, discounted)]

    def _calculate_discount(self, item):
        return item.price * 0.1 if item.quantity > 10 else 0

    def _format_receipt(self, item, discount):
        return f"{item.name}: {item.price - discount}"
```

### When Local Functions Need Closure State

If a local function would close over variables from the parent scope, extracting to a class method requires passing that state. Use `functools.partial` to bind the extra args:

```python
from functools import partial


class Processor:
    def process(self, items, config):
        # bind config via partial, so _transform matches the expected callback signature
        report = framework.handle(
            items, transform=partial(self._transform, config=config)
        )
        return report

    def _transform(self, item, *, config):
        return {**item, "adjusted": item["value"] * config.factor}
```
