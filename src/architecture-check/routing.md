# 🧭 Route the proposed change

Inspect the project tree and read a comparable flow from its entry point to its result. For each changed responsibility, identify who makes the decision, what data crosses the boundary and which module already owns it. Extend an existing owner when it fits. Create a file or directory when the change introduces a distinct responsibility. In an empty repository, derive the smallest set of modules from the requested flow.

## Placement matrix

Choose the parent directory for each module as part of the placement decision. Look at the siblings that will sit beside it. In the defect ETL, the package immediately below `pipelines/` names a data stage. Within Silver, the next directory names a capability or tenant scope. Inside that scope, `core/` owns computations and `registry/` owns declarations. Shared mechanisms have a different organizing principle. This excerpt shows how the two groupings coexist.

```text
src/data_pipeline/
├── shared/
│   ├── core/ports/table_store.py
│   ├── application/pipeline_runner.py
│   └── infrastructure/delta/delta_table_store.py
└── pipelines/silver/
    ├── canonical/registry/schemas.py
    └── tenants/tenant_a/
        ├── core/
        │   ├── normalize_defects.py
        │   └── normalize_work_orders.py
        └── registry/
            ├── schemas.py
            ├── status_mapping.py
            └── steps.py
```

For a new workflow, sketch the smallest tree that makes its real ownership groups visible. Place related modules together and let independent capabilities grow separately. Add another nesting level only when it identifies a meaningful subgroup. Use the target project's language for these directories.

Use the final defect ETL design as a worked example. Paths below are relative to its illustrative `src/data_pipeline/` package. Choose names and boundaries from the target repository.

Place technology dependencies using these criteria.

- Default to infrastructure. Put the API behind an adapter when the application can express the capability in its own terms. A Codex CLI subprocess and an AWS Secrets Manager call are typical examples.
- Admit a framework into core when the project has an established convention and the cost of abstracting its API justifies that choice.

In this ETL example the company has standardized hundreds of pipelines on Spark. Transformations are written in Spark's DataFrame language. A framework-neutral adapter for those expressions would need to reproduce a substantial part of that language, with little expected benefit from switching engines. This convention allows Spark expressions and DataFrame validation in core. Delta persistence still has a narrow read/write contract. In another project, establish its own convention before applying this exception to Spark, pandas or another framework.

| Responsibility in the patch | Placement rule | Defect ETL example |
| --- | --- | --- |
| Decide what a domain outcome means | Keep the decision or lookup with the domain that defines it. The application passes the decided value to the outbound port. | Tenant status mappings belong with the tenant's Silver rules. The Delta writer persists the resulting data. |
| Define the data and step vocabulary | Keep shared types with the contracts their callers use. | `shared/core/models/table.py` pairs a qualified name with a schema. `pipeline_step.py` describes named inputs, outputs, contracts and a transformation. |
| Check a data contract | Keep the check beside the contract when the data representation is an accepted core dependency. | `shared/core/schema_validation.py` validates Spark DataFrames directly. |
| Coordinate operations | Keep ordering in the application runner. | `shared/application/pipeline_runner.py` reads, validates inputs, transforms, validates outputs and writes. |
| Access an external system | Put the required capability in a port when callers need a boundary. Put commands, SDK calls and storage protocols in the concrete adapter. | `shared/core/ports/table_store.py` describes DataFrame reads and writes. `shared/infrastructure/delta/delta_table_store.py` implements Delta access. |
| Declare inputs, outputs and mappings | Put declarations in the narrowest registry that owns them. | Bronze metrics and tenant registries declare copy steps and schemas. `pipelines/silver/canonical/registry/schemas.py` owns shared defect and work-order contracts. Tenant registries own their status mappings. |
| Transform data | Scope calculations to the stage and tenant whose rules they implement. | Silver tenant `core/normalize_defects.py` emits canonical defects and tenant details. `normalize_work_orders.py` handles work orders. Silver metrics owns `prepare_metrics.py`. |
| Enrich and present results | Keep the shared join separate from tenant-specific report selection and naming. | `pipelines/gold/enrichment/core/enrich_defects.py` joins defects with metrics. `pipelines/gold/reports/tenants/tenant_a/core/build_defect_report.py` combines Gold with Silver details. |
| Resolve deployment values and wire dependencies | Resolve settings in configuration, assemble concrete collaborators at startup and invoke the flow from its entry point. | `configuration/environment.py` resolves the catalog prefix. `configuration/registry/tables.py` declares external and internal tables. `bootstrap.py` wires steps, tables, runner and Delta adapter. `entrypoints/run_pipeline.py` starts execution. |

For example, a change to Tenant B's source statuses can use Tenant A's status registry as placement evidence. A new external sink may require a new adapter. Trace which runner calls it, the data it receives and where bootstrap selects the implementation before choosing its path.
