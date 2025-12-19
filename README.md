# dbt column lineage

This project computes the column lineage of the dbt testing project [jaffle_shop](https://github.com/dbt-labs/jaffle_shop_duckdb) thanks to [SQLGlot](https://sqlglot.com/sqlglot.html).

## Example

### dbt model

As an example of the lineage, let's take the model `stg_orders` and the output column `customer_id`:

* first CTE imports all columns from the source with a `select *`
* column `user_id` is renamed to `customer_id` in a followinf CTE
* finally, the last select is also a `select *` from the renaming CTE

➡️ column name is not explicit in the import, neither in the export, and column name output differs from input

```sql
with source as (

    select * from {{ ref('raw_orders') }}

),

renamed as (

    select
        id as order_id,
        user_id as customer_id,
        order_date,
        status

    from source

)

select * from renamed
```

### Computed lineage

The [script](./main.py) has been run on the whole dbt project and produced its columns lineage [as this json file](./jaffleshop_lineage.json).

This is the extract of the lineage for `customer_id`:

```json
{
   "customer_id":{
      "intermediate_columns":[
         "customer_id",
         "renamed.customer_id",
         "source.user_id",
         "*"
      ],
      "ancestor_columns":[
         {
            "db":"main",
            "catalog":"jaffle_shop",
            "table":"raw_orders",
            "column":"user_id"
         }
      ]
   }
}
```

As expected, we get:

* the final column output is `customer_id`
* intermediate column names are `*`, `user_id`, and `customer_id`
* the ancestor column is `user_id`, from the database `main`, dataset `jaffle_shop`, table `raw_orders` 

_Now time to traverse all child nodes using dbt table lineage_ 🔥

## Setup

Instructions to reproduce locally or test it with your own `manifest.json` =)

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
