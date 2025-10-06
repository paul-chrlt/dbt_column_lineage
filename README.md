# dbt_column_lineage

This project explores the column lineage of the dbt testing project [jaffle_shop](https://github.com/dbt-labs/jaffle_shop_duckdb), using duckdb to allow for locally reproducible code.

## Setup

### dbt project

Install the dbt project using the instructions in the [jaffle_shop](https://github.com/dbt-labs/jaffle_shop_duckdb) repo:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
source venv/bin/activate
```

Then run the dbt project to generate a `manifest.json`:

```bash
dbt build
```

You should now have a manifest.json in the `target` folder.

Deactivate the jaffle_shop virtual environment:

```bash
deactivate
```
