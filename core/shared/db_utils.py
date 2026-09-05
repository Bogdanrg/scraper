from typing import Any

import sqlalchemy as sa


def generate_equality_sql_expression(model, where_fields: dict[str, Any]):
    """
    Generates sql expression for equality for input model from input dict where:
     keys - name of model's fields,
     values - values with what those fields need to be equal.
    """
    if not where_fields:
        return sa.true()

    result = []

    for k, v in where_fields.items():
        if not hasattr(model, k):
            raise ValueError(f'Key `{k}` not found in data model')

        model_field = getattr(model, k)
        result.append(model_field.in_(v) if isinstance(v, (list, tuple)) else model_field == v)

    return sa.and_(True, *result)
