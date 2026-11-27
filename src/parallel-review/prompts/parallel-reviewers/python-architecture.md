# Python architecture

Apply the rules below for dependency direction and package ownership. Ground each finding in a visible import, call, type, or path.

## Dependency direction

- Keep business decisions and transformations in the core. Identify them by what result they compute. A transformation can operate on a data frame supplied by its caller.
- At an entry point, translate invocation arguments into one application call and present its result. Trace the sequence another caller would have to repeat. Flag use-case steps or concrete source reads found in the entry point.
- An API may import core types and call core functions. Flag a core module that imports an API handler or accepts a framework request purely to extract domain inputs.
- When an invocation supplies data directly, pass that value to the application. When it supplies a reference and the use case requires retrieval, check that the application calls a source port and the concrete adapter performs the I/O.
- Keep infrastructure-specific reads, writes, and conversions in adapters. This applies to any external system, including storage and identity services.
- Select the adapter where the application is assembled.
- Use a substitution check: if another implementation provided the same operation, which lines of business logic would have to change? Flag a concrete dependency when the supplied code shows that a backend swap would require editing a business decision or transformation.

## Package ownership

- Group core decisions, port contracts, and adapters by responsibility when the code actually has those boundaries. A directory name alone does not establish dependency inversion.
- Keep model definitions with the layer that owns their meaning. For example, domain decisions can live in `core/models.py` and transport payloads in `api/models.py`. Flag a shared models module when it couples otherwise independent layers. A small project can have a single model owner.
- When sibling filenames repeat a meaningful prefix, check whether it names a coherent package. Recommend moving the files into that package and dropping the prefix only when the visible siblings share that responsibility.
