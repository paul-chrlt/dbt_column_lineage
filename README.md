# dbt_column_lineage

This project explores the column lineage of the dbt testing project [jaffle_shop](https://github.com/dbt-labs/jaffle_shop_duckdb), using duckdb to allow for locally reproducible code.

## Setup

### dbt project

If you cloned this repository, git will not clone the jaffle_shop submodule by default:
```bash
cd ./jaffle_shop_duckdb/
git submodule init
git submodule update
```

Install the dbt project using the instructions in the [jaffle_shop](https://github.com/dbt-labs/jaffle_shop_duckdb) repo:

_Installation had pydantic-core issues with python3.14, I had to use python 3.9_
```bash
cd ./jaffle_shop_duckdb/
python3.9 -m venv dbt_jaffle_shop_venv
source dbt_jaffle_shop_venv/bin/activate
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt
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
### column lineage

Create a dedicated env with dependencies

```
python3 -m venv dbt_column_lineage_venv
source dbt_column_lineage_venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

You can now execute the script on the manifest you just created
```
python3 ./main.py
```

This will generate a `dbt_lineage.json` file containing the whole column lineage of this dbt project.

As an example, for the model `stg_orders` and the output column `customer_id`:

* first select is a `select *`
* a cte then renames `user_id` to `customer_id`
* finally, the last select is also a `select *`

For this example, here is what we can find in the lineage (full output: `jaffleshop_lineage.json`):
````json
{
   "intermediate_columns":{
      "*",
      "customer_id",
      "renamed.customer_id",
      "source.user_id"
   },
   "ancestor_columns":[
      {
         "db":"main",
         "catalog":"jaffle_shop",
         "table":"raw_orders"
      }
   ]
}
#@todo: include first known column name in ancestor_column
```
