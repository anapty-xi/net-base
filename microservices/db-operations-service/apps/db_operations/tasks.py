import pathlib
import pandas as pd
from datetime import datetime

from logging import getLogger
from config.celery import app
from .usecases.table_usecases import TableInfo, GetRows
from .infrastructure.repository_manager import RepositoryManager


logger = getLogger(__name__)

@app.task
def db_dump():
    from config.pool import DB_ENGINE
    schema_repository_manager = RepositoryManager(DB_ENGINE)
    schema_usecase = TableInfo(schema_repository_manager)

    tables_schemas = schema_usecase.execute()
    if tables_schemas:
        path = pathlib.Path(f'{pathlib.Path.home()}/db_dumps/{str(datetime.now().date())}')
        path.mkdir(parents=True, exist_ok=True)
        for title, cols in tables_schemas.items():
            rows_repository_manager = RepositoryManager(DB_ENGINE)
            rows_usecase = GetRows(rows_repository_manager)
            rows = rows_usecase.execute(title, None)

            df = pd.DataFrame(rows, columns=cols)
            file_path = path / 'title.xsxl'
            df.to_excel(file_path, index=False)
            logger.info(f'таблица {title} была сохрынена в fs')


            
    
    logger.error('Небыло сохранено ни одной таблицы')

