from unittest.mock import patch

import pytest

from dbttoolkit.documentation.models.column import ColumnDescriptionWithSource
from dbttoolkit.documentation.presentation.formatters import (
    format_node_link_in_markdown,
    format_upstream_descriptions_to_human_readable,
)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            "model.project.model_path.model_name",
            "[model.project.model_path.model_name](/#!/model/model.project.model_path.model_name)",
        ),
        (
            "source.project.source_path.source_name",
            "[source.project.source_path.source_name](/#!/source/source.project.source_path.source_name)",
        ),
    ],
    ids=["model", "source"],
)
def test_format_node_link_in_markdown(test_input, expected):
    assert format_node_link_in_markdown(test_input) == expected


class TestFormatUpstreamDescriptionsToHumanReadable:
    @pytest.mark.parametrize(
        "test_input,expected_output",
        [
            (
                "description_from_upstream_simple",
                "description in source1 [propagated from source1]\n\ndescription in source2 [propagated from source2]",
            ),
            ("description_from_upstream_common", "common description [propagated from source1, source2]"),
        ],
    )
    def test_simple(self, test_input, expected_output, request):
        test_input = request.getfixturevalue(test_input)

        output = format_upstream_descriptions_to_human_readable(test_input)
        assert output == expected_output

    @pytest.fixture()
    def description_from_upstream_simple(self) -> ColumnDescriptionWithSource:
        return {
            "source1": "description in source1",
            "source2": "description in source2",
        }

    @pytest.fixture()
    def description_from_upstream_common(self) -> ColumnDescriptionWithSource:
        return {
            "source1": "common description",
            "source2": "common description",
        }

    @pytest.fixture(autouse=True, scope="class")
    def mocked_link_formatter(self):
        """Convenience patch so the strings in the output are more readable"""
        with patch(
            "dbttoolkit.documentation.presentation.formatters.format_node_link_in_markdown",
            side_effect=lambda node_id: node_id,
        ):
            yield
