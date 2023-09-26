# dbt documentation propagation

Propagates dbt documentation for columns that are documented and have the same name in downstream dependencies.

> Example: A dbt model `user` has a column called `name`, which is documented. Another dbt model `user_stats`
> depends on `user` and also has a column called `name`, which is not documented. This automation will
> propagate (i.e., "pass along") the documentation from `user.name` to `user_stats.name`.

Example:

<p align="center">
    <a href="https://github.com/voi-oss/dbt-toolkit/blob/main/docs/propagation_simple.png">
        <img 
          src="https://github.com/voi-oss/dbt-toolkit/blob/main/docs/propagation_simple.png?raw=true" 
          alt="Propagation example"
          width="600px"
        />
    </a>
</p>

Currently, the documentation is propagated by modifying the `manifest.json`, and not by editing the
existing `schema.yml` files.

## Features

* The documentation is propagated from upstream models (or sources) to downstream dependencies for columns with the same
  name.
* The propagation happens recursively. It can go
  from `source (documented) -> child (undocumented) -> grandchild (undocumented)`, no matter how many levels deep.
* A downstream dependency that renamed a column (e.g.: from `id` to `user_id`) can specify the original column name as a
  meta property and still have the documentation propagated even if the name of the column has changed.
* The propagated documentation automatically includes a link to the node where the documentation was defined.
* If a column can inherit documentation from multiple upstream columns (because they all have the same name), all
  documentation will be included.
* The columns that have most downstream dependencies but are not documented are listed (i.e. which columns would benefit
  the most from this automation if they are documented)

### Column renaming

If a source `user` has a column called `id` and a downstream model `stg_user` has a column `user_id` and we want the
documentation from the former to be propagated to the latter, the following meta property can be used:

```yaml
models:
  - name: stg_user
    columns:
      - name: user_id
        meta:
          original_name: id
```

Note that if `stg_user` has multiple upstream models with documented columns with the name `id`, all of them will be
inherited.

### Features roadmap

* Propagation from ephemeral models to models and between macros has not been tested yet
* Check if it works for columns documented in the source that does not exist in the warehouse (i.e. if we go with a
  raw `json` strategy)
* What happens if 3 upstream columns have the same documentation. Are we repeating all 3?
* Write a test for capturing the behavior of multiple inheritance on different levels:

```
Source1 (YES) --------------->  Target (NO)
Source2 (YES) -> Model2 (NO)  /
```

---

## How does it work

The following dbt artifacts are used as input:

* `catalog.json` to get all the columns available in the objects (tables and views) in the data warehouse
* `manifest.json` to get the existing project documentation

They are parsed and all columns are combined on a data structure, which is recursively traversed to identify the columns
with the same name that are part of the same dependency graph. The propagated column documentation is then written back
to the `manifest.json`.
