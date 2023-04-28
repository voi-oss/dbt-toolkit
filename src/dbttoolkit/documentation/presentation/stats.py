from collections import namedtuple
from typing import List

from dbttoolkit.documentation.models.column import ColumnRegistry
from dbttoolkit.utils.logger import get_logger

logger = get_logger()

PotentialPropagation = namedtuple("PotentialPropagation", ["parent", "children"])


def calculate_and_print(registry: ColumnRegistry) -> None:
    """
    Calculate some basic statistics (total number of parsed columns, how many are documented, etc) and
    which columns would benefit the most from being documented.
    """
    logger.info(f"Total columns: {len(registry.data.keys())}")

    columns_without_docs = [column for column in registry.data.values() if not column.description]
    columns_with_docs = [column for column in registry.data.values() if column.description]
    logger.info(f"👍 With docs: {len(columns_with_docs)} ({len(columns_with_docs) / len(registry.data.keys())})")
    logger.info(
        f"👎 Without docs: {len(columns_without_docs)} ({len(columns_without_docs) / len(registry.data.keys())})"
    )

    columns_can_receive_propagation = [
        column for column in registry.data.values() if column.descriptions_from_upstream and not column.description
    ]
    logger.info(f"✅ Columns with documentation propagated: {len(columns_can_receive_propagation)}")

    best_columns_to_be_documented = _find_best_columns_to_be_documented(registry)
    logger.info(f"🕵 Can propagate documentation if documented: {len(best_columns_to_be_documented)}")

    if best_columns_to_be_documented:
        logger.info("\n=> Top 25:")

        logger.info(
            "\n".join(
                [
                    f"{potential.parent} ({len(potential.children)}) => {potential.children}"
                    for potential in best_columns_to_be_documented[0:25]
                ]
            )
        )


def _find_best_columns_to_be_documented(registry: ColumnRegistry) -> list:
    """
    Retrieves which columns are not documented but would benefit the most if documented (i.e. propagating its
    documentation would affect most downstream columns).
    """
    best_columns_to_be_documented: List[PotentialPropagation] = []

    for column in registry.data.values():
        if column.upstream_matches:
            # We only want nodes without parents, because otherwise we would be repeating nodes
            continue

        if column.description:
            # And not currently documented
            continue

        children = [column for column in column.downstream_matches_recursive if not column.description]

        if len(children) == 0:
            # Wouldn't be propagated anywhere
            continue

        best_columns_to_be_documented.append(PotentialPropagation(column, children))

    best_columns_to_be_documented.sort(key=lambda potential: len(potential.children))
    best_columns_to_be_documented.reverse()

    return best_columns_to_be_documented
