# Python architecture

Review the supplied changes for dependency direction and package ownership. Ground each finding in a visible import, call, type, or path.

## Dependency direction

- Keep business decisions in the core. Translate CLI arguments, HTTP payloads, or hook events at the entry point. An API may import core types and call core functions. Flag a core module that imports an API handler or accepts a framework request purely to extract domain inputs.
- Define a port around the operation the core needs. Pass that contract into the core. Keep subprocess calls, network requests, and provider-specific serialization inside concrete adapters. Select the adapter where the application is assembled.
- Check that providers are interchangeable through the same port. For example, switching a classifier from Codex to Jev should require changing the selected adapter. If it also requires editing the core decision or branching there on provider names, identify that dependency.

## Package ownership

- Group core decisions, port contracts, and adapters by responsibility when the code actually has those boundaries. A directory name alone does not establish dependency inversion.
- Keep model definitions with the layer that owns their meaning. For example, domain decisions can live in `core/models.py` and transport payloads in `api/models.py`. Flag a shared models module when it couples otherwise independent layers. A small project can have a single model owner.
- When sibling filenames repeat a meaningful prefix, check whether it names a coherent package. For example, `classifiers/codex.py` and `classifiers/jev.py` express the relationship between `classifier_codex.py` and `classifier_jev.py`. Recommend the move only when the visible siblings have that shared responsibility.
