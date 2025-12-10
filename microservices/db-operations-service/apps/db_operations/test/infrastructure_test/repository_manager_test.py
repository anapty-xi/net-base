import pytest

from unittest.mock import patch
from sqlalchemy import create_engine, text, MetaData, String, insert, select
from apps.db_operations.infrastructure.repository_manager import RepositoryManager
from apps.db_operations.entities.table import Table
from sqlalchemy.schema import Table as AlchemyTable
from sqlalchemy.schema import Column
from sqlalchemy.exc import OperationalError

test_engine = create_engine('sqlite:///:memory:', echo=False)
metadata = MetaData()

class TestRepositoryManager:
    def setup_method(self):
        self.rep_manager = RepositoryManager(test_engine)

    def test_create_table_and_insert_rows(self):
        test_table = Table(
            title='test',
            cols=['col1', 'col2', 'col3'],
            rows=[
                ['row11', 'row12', 'row13'],
                ['row21', 'row22', 'row23']
            ],
            in_analytics=False
        )

        self.rep_manager.create_table(test_table)

        with test_engine.connect() as conn:
            result = conn.execute(text('SELECT * FROM test'))
            rows = result.fetchall()

            assert len(rows) == 2
            assert rows[0] == (1, 'row11', 'row12', 'row13')

    def test_get_table_info(self):
        test_table = self.rep_manager.get_table_info(title='test')
        assert len(test_table) == 1 
        assert 'test' in test_table.keys()
        assert ['id', 'col1', 'col2', 'col3'] == test_table['test']

    def test_get_all_tables(self):
        columns = [Column('coll1', String, nullable=True), Column('coll2', String, nullable=True)]
        new_table = AlchemyTable(
            'test2',
            metadata,
            *columns
        )
        metadata.create_all(test_engine)
        tables_info = self.rep_manager.get_table_info(title=None)
        assert len(tables_info) == 2
        assert 'test' in tables_info.keys() and 'test2' in tables_info.keys()
        assert ['id', 'col1', 'col2', 'col3'] == tables_info['test'] and ['coll1', 'coll2'] == tables_info['test2']

    def test_update_row(self):
        self.rep_manager.update_row('test', '1', {'col1': 'строка1'})
        with test_engine.connect() as conn:
            result = conn.execute(text('SELECT * FROM test WHERE id == 1'))
        row = result.fetchall()
        assert row[0][1] == 'строка1'

    def test_delete_table(self):
        self.rep_manager.delete_table('test')
        try:    
            with test_engine.connect() as conn:
                conn.execute(text('SELECT * FROM test WHERE id == 1'))
            assert False
        except OperationalError:
            assert True

    def test_get_rows(self):
        table = AlchemyTable('test2', metadata, autoload_with=test_engine)
        data = [{'coll1': 'row1', 'coll2': 'row2'}, {'coll1': 'row3', 'coll2': 'row4'}]
        with test_engine.connect() as conn:
            conn.execute(insert(table), data)

        query = {'coll1': 'row1'}

        with test_engine.connect() as conn:
            result = conn.execute(select(table).where(table.columns['coll1'] == 'row1'))
        rows = result.fetchall()
        assert [list(row) for row in rows] == self.rep_manager.get_rows('test2', query)
