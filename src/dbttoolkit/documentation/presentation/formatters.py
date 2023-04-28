from typing import Dict, List

from dbttoolkit.documentation.models.column import ColumnDescriptionWithSource


def format_node_link_in_markdown(node_id: str) -> str:
    """
    Returns a Markdown-formatted link
    """
    node_type = node_id.split(".")[0]

    return f"[{node_id}](/#!/{node_type}/{node_id})"


def format_upstream_descriptions_to_human_readable(descriptions_from_upstream: ColumnDescriptionWithSource) -> str:
    # To achieve a deterministic outcome, we sort the descriptions by node_id
    sorted_descriptions = {k: v for k, v in sorted(descriptions_from_upstream.items(), key=lambda item: item[0])}

    # Invert the dict. Description becomes the keys and the sources the values
    inverted_descriptions: Dict[str, set] = {}

    for node_id, description in sorted_descriptions.items():
        inverted_descriptions.setdefault(description, set()).add(node_id)

    output: List[str] = []

    for description, node_ids in inverted_descriptions.items():
        nodes = [format_node_link_in_markdown(node_id) for node_id in node_ids]

        description += f' [propagated from {", ".join(sorted(nodes))}]'
        output.append(description)

    return "\n\n".join(output)
