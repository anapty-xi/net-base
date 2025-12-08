import pytest

from ...usecases import table_usecases
from unittest.mock import patch, Mock


@patch('apps.db_operations.usecases.table_usecases.TableValidator')
def test_create_table_usecase(mock_validator_class):
    mock_validator = Mock()
    mock_validator.validate_table.side_effecte = lambda table: table
    mock_validator.return_value = mock_validator

    mock_infrastructure = Mock()
    mock_infrastructure.create_table.return_value = True

    use_case = table_usecases.CreateTable(mock_infrastructure)

    result = use_case.execute(
        title="users",
        cols=["name", "email"],
        rows=[["Alice", "alice@example.com"]],
        in_analytics=True
    )

    assert result is True


    mock_validator_class.assert_called_once()
    mock_validator.validate_table.assert_called_once()
