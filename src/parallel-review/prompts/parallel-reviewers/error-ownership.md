# Error ownership and translation

Apply these checks to changed failure paths. Follow a failure from its origin to the caller that handles it.

- **Find the owner.** A business invariant belongs with its domain rule. A failed use-case precondition or unavailable capability belongs with the use case or port that defines its meaning. An adapter can raise or catch these inward-owned errors.
- **Check dependency direction.** Flag inner code that imports provider exceptions or assumes a particular input source, transport or caller in its error contract.
- **Preserve failures.** Preserve a meaningful failure through intermediate layers.
- **Check outbound translation.** At an outbound port, translate implementation failures when the consumer needs a stable contract.
- **Check entry-point translation.** At an entry point, map failures to the response, exit behavior or job outcome its actual caller expects. Preserve safe diagnostic context while keeping sensitive details out of public responses.
- **Check catch-alls.** Report a catch-all that hides a distinction required for recovery or reporting. Ground the finding in a concrete caller or declared contract.
- **Check wrappers.** Report a wrapper that merely renames a failure. Ground the finding in a concrete caller or declared contract.
- **Check failure types.** A common error type can suffice when callers handle the failures alike.
