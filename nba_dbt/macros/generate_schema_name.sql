{#
  Overrides dbt's default generate_schema_name behaviour.

  By default dbt concatenates the target dataset and the custom schema
  (e.g. "nba_dbt_nba_gold"), which is not what we want.  This macro
  returns the custom schema name verbatim when one is supplied, so that
  +schema: nba_silver  →  BigQuery dataset nba_silver
  +schema: nba_gold    →  BigQuery dataset nba_gold
  If no custom schema is set the target dataset from profiles.yml is used
  as the fallback, preserving dbt's normal behaviour for untagged models.
#}

{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.dataset }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
