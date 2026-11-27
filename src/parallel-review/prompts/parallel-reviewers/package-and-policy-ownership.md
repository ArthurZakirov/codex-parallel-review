# Package and policy ownership

Apply these rules when reviewing where modules and decisions belong.

- **Trace decisions across ports.** Locate each domain rule, including instructions stored as text and outcome-to-action tables. Check that core owns the rule, application code coordinates its use, and the concrete adapter receives the decided action.
- **Check transport lookup ownership.** Transport-specific lookup of an external identifier for a supplied target belongs in the adapter.
- **Check root placement.** For a new single-entry executable, inspect every root-level source path. Flag implementation modules beside the launch script and identify their package owners. Review root-level metadata according to its tooling conventions.
