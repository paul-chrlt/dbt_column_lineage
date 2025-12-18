import json
import re
import pandas as pd

from sqlglot import parse_one, exp
from sqlglot.lineage import lineage
from sqlglot.errors import SqlglotError

# vars
manifest_path = './jaffle_shop_duckdb/target/manifest.json'
parsing_dialect = 'duckdb'
lineage_export_path = "./dbt_lineage.json"

# importing manifest
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

# cleaning: nodes and sql queries
dbt_lineage = dict()

for node_key, node_val in manifest['nodes'].items():
    dbt_lineage[node_key] = {
        'dbt_project': node_val.get('database'),
        'dbt_schema': node_val.get('schema'),
        'dbt_resource_name': node_val.get('name'),
        'dbt_resource_type': node_val.get('resource_type'),
        'sql_query': node_val.get('compiled_code'),
        'dbt_columns': list(node_val.get('columns', {}).keys())
    }

# debug, sample
# id, user_id, order_date, status
# from jaffleshop.main.raw_orders
# order_id, customer_id, order_date, status
# dbt_lineage = {key: value for key, value in dbt_lineage.items() if key == 'model.jaffle_shop.stg_orders'}

# compute lineages

for node_key in dbt_lineage:

    if 'sql_query' not in dbt_lineage[node_key].keys():
        continue

    sql_query = dbt_lineage[node_key]['sql_query']
    
    if sql_query is None:
        continue
    if len(sql_query.split()) == 0:
        continue

    parsed_expression = parse_one(
        sql = sql_query,
        dialect = parsing_dialect
    )

    dbt_lineage[node_key]['columns'] = dict()

    # get all select expressions. Last one is the final select
    selects = parsed_expression.find_all(exp.Select)
    final_select = list(selects)[-1]
    final_select_columns = [select_column.output_name for select_column in final_select.expressions]

    for column_name in final_select_columns:
        if column_name == '*':
            continue
        try:
            node_lineage = lineage(column_name, sql_query, dialect=parsing_dialect)
        # except Exception as e:
        except SqlglotError as e:
            print(f"Error computing lineage for {node_key}.{column_name}")
            continue
        upstream_elements = list()
        element_ancestors = list()
        i=0
        for element in node_lineage.walk():
            element_name = element.name
            if element.name != "*":
                debug_element = element
            upstream_elements.append(element.name)
            table = element.expression.find(exp.Table)
            if element.expression.find(exp.Table):
                element_ancestors.append({
                        "db":table.db,
                        "catalog":table.catalog,
                        "table":table.name,
                        "column":upstream_elements[-2].split(".")[-1]
                    })
            i+=1
        
        dbt_lineage[node_key]['columns'][column_name] = {
            'intermediate_columns': upstream_elements,
            'ancestor_columns': element_ancestors
        }

# export downstream elements of all queries
with open(lineage_export_path, "w") as f:
    json.dump(dbt_lineage, f, default = list)

# transform to table
lineage_table = pd.DataFrame.from_dict(dbt_lineage, orient = "index")

# export

