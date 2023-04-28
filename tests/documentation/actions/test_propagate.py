import json
import tempfile
from pathlib import Path
from typing import Mapping

import pytest

from dbttoolkit.documentation.actions import propagate


@pytest.fixture(scope="module")
def transformed_artifact(dbt_sample_project_path: Path):
    with tempfile.NamedTemporaryFile() as tmpfile:
        propagate.run(dbt_sample_project_path / "target", "manifest_original.json", Path(tmpfile.name))

        yield json.load(tmpfile)


def test_propagation_1_level(transformed_artifact: Mapping):
    """
    Parent (with documentation) -> child (without documentation) propagation works
    """
    description = column_description(transformed_artifact, "stg_user", "name")

    assert (
        description == "Name column of the user table in the source. "
        "[propagated from [source.dbt_sample_project.raw.user]"
        "(/#!/source/source.dbt_sample_project.raw.user)]"
    )


def test_propagation_2_level(transformed_artifact: Mapping):
    """
    Parent (with documentation) -> child (without documentation) -> grandchild (without documentation)
    propagation works. The first parent is listed as source.
    """
    description = column_description(transformed_artifact, "mart_user", "name")

    assert (
        description == "Name column of the user table in the source. "
        "[propagated from [source.dbt_sample_project.raw.user]"
        "(/#!/source/source.dbt_sample_project.raw.user)]"
    )


def test_ignored_columns(transformed_artifact: Mapping):
    """
    Some columns can be globally ignored (example: id)
    """
    description = column_description(transformed_artifact, "stg_user", "id")

    assert description == ""


def test_alias(transformed_artifact: Mapping):
    """
    Children can specify a meta attribute for renamed columns
    """
    original_description = column_description(transformed_artifact, "raw.user", "height", node_type="source")
    propagated_description = column_description(transformed_artifact, "stg_user", "height_cm")

    assert original_description is not None
    assert (
        propagated_description
        == original_description
        + " [propagated from [source.dbt_sample_project.raw.user](/#!/source/source.dbt_sample_project.raw.user)]"
    )


def test_2_parents(transformed_artifact: Mapping):
    """
    A column can inherit documentation from more than one parent. Note here that they are even on different levels
    """

    description = column_description(transformed_artifact, "mart_user_and_city", "name")

    expected = (
        "Name column of the city table in the source. "
        "[propagated from [source.dbt_sample_project.raw.city]"
        "(/#!/source/source.dbt_sample_project.raw.city)]"
        "\n\n"
        "Name column of the user table in the source. "
        "[propagated from [source.dbt_sample_project.raw.user]"
        "(/#!/source/source.dbt_sample_project.raw.user)]"
    )

    assert description == expected


"""
Helper functions
"""


def column_description(artifact: Mapping, node_name: str, column_name: str, *, node_type: str = "model"):
    """
    Retrieves the description of a column on a node given an artifact.
    The node type can be both a model (default) or a source.
    """
    if node_type == "model":
        node = artifact["nodes"][f"model.dbt_sample_project.{node_name}"]
    elif node_type == "source":
        node = artifact["sources"][f"source.dbt_sample_project.{node_name}"]
    else:
        raise NotImplementedError(f"Unexpected {node_type}")

    return node["columns"][column_name]["description"]
