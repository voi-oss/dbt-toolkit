from enum import Enum


class DbtArtifact(str, Enum):
    """
    The built-in dbt artifacts
    """

    catalog = "catalog"
    manifest = "manifest"
    run_results = "run_results"
    sources = "sources"
