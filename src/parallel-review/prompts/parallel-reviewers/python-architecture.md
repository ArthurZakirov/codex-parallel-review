# Python architecture

Apply the rules below for dependency direction and package ownership. Ground each finding in a visible import, call, type, or path.

## Dependency direction

- Keep business decisions and transformations in the core. Identify them by what result they compute. A transformation can operate on a data frame supplied by its caller.
- Translate external inputs into the values those decisions need at the entry point.
- An API may import core types and call core functions. Flag a core module that imports an API handler or accepts a framework request purely to extract domain inputs.
- When the core must call an external capability, define a port around the operation it needs and supply an implementation. When the caller can perform the I/O before or after a pure transformation, passing the data directly is sufficient.
- Keep infrastructure-specific reads, writes, and conversions in adapters. This applies to any external system, including storage and identity services.
- Select the adapter where the application is assembled.
- Use a substitution check: if another implementation provided the same operation, which lines of business logic would have to change? Flag a concrete dependency when the supplied code shows that a backend swap would require editing a business decision or transformation.

## Package ownership

- Group core decisions, port contracts, and adapters by responsibility when the code actually has those boundaries. A directory name alone does not establish dependency inversion.
- Keep model definitions with the layer that owns their meaning. For example, domain decisions can live in `core/models.py` and transport payloads in `api/models.py`. Flag a shared models module when it couples otherwise independent layers. A small project can have a single model owner.
- When sibling filenames repeat a meaningful prefix, check whether it names a coherent package. Recommend moving the files into that package and dropping the prefix only when the visible siblings share that responsibility.
