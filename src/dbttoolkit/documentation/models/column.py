from collections import namedtuple
from typing import Any, Dict, Mapping, Optional, Set

from pydantic import BaseModel, Field

ColumnFqn = namedtuple("ColumnFqn", ["node_id", "name"])

ColumnDescriptionWithSource = Dict[str, str]  # { 'node_id': 'description' }


class Column(BaseModel):
    """
    A column that exists in a dbt model. An common representation for both dbt catalog and dbt manifest columns.

    It has pointers to the node object from the artifact and also the original column object.
    Also has pointers to upstream and downstream dependencies and methods to recurse through them.
    """

    name: str = Field(..., allow_mutation=False)
    node: Mapping = Field(..., allow_mutation=False, repr=False)

    artifact_column: Mapping  # Can be either the column representation in the manifest or in the catalog
    description: Optional[str]

    upstream_matches: Set = set()
    downstream_matches: Set = set()

    class Config:
        validate_assignment = True

    def __post__init__(self) -> None:
        if self.description == "":
            self.description = None

    def add_upstream_match(self, column: "Column") -> None:
        self.upstream_matches.add(column)

        if self not in column.downstream_matches:
            column.add_downstream_match(self)

    def add_downstream_match(self, column: "Column") -> None:
        self.downstream_matches.add(column)

        if self not in column.upstream_matches:
            column.add_upstream_match(self)

    @property
    def downstream_matches_recursive(self) -> set:
        output = set()

        for column in self.downstream_matches:
            output.add(column)
            output.update(column.downstream_matches_recursive)

        return output

    @property
    def descriptions_from_upstream(self) -> ColumnDescriptionWithSource:
        """
        :return: dict with node_id as key and original description as value
        """
        descriptions = {}

        for column in self.upstream_matches:
            if column.description:
                descriptions[column.node_id] = column.description
            else:
                # Only search up if it was not found already
                for node_id, description in column.descriptions_from_upstream.items():
                    descriptions[node_id] = description

        return descriptions

    @property
    def node_id(self) -> str:
        return self.node["unique_id"]

    @property
    def fqn(self) -> ColumnFqn:
        return ColumnFqn(self.node_id, self.name)

    def __hash__(self):
        return hash(self.fqn)

    def __eq__(self, other: Any):
        return isinstance(other, self.__class__) and self.fqn == other.fqn

    def __repr__(self):
        model_type = self.fqn.node_id.split(".")[0]
        friendly_model_name = ".".join(self.fqn.node_id.split(".")[2:])
        return f"[{model_type}] {friendly_model_name}.{self.fqn.name}"

    def __str__(self):
        return self.__repr__()

    @classmethod
    def build_from_dbt_manifest_column(cls, column: Mapping, node: Mapping) -> "Column":
        return cls(name=column["name"].lower(), node=node, description=column["description"], artifact_column=column)

    @classmethod
    def build_from_dbt_catalog_column(cls, column: Mapping, node: Mapping) -> "Column":
        return cls(name=column["name"].lower(), node=node, artifact_column=column)


class ColumnRegistry(BaseModel):
    """
    A data structure to make it easy to work with dbt column representations.

    It has a simple internal data structure that maps column unique identifiers to their dbt representation, and it
    provides a convenience method to add or retrieve column definitions both from the manifest and the catalog.
    """

    data: Dict[ColumnFqn, Column] = {}

    def add_or_retrieve(self, *, column_in_manifest: dict = None, column_in_catalog: dict = None, node) -> Column:
        if column_in_manifest:
            column = Column.build_from_dbt_manifest_column(column_in_manifest, node)
        elif column_in_catalog:
            column = Column.build_from_dbt_catalog_column(column_in_catalog, node)
        else:
            raise ValueError("Invalid column details")

        return self.data.setdefault(column.fqn, column)
