import logging

from typing import List, Self, Annotated
from pydantic import BaseModel, model_validator, AfterValidator

logger = logging.getLogger(__name__)

def validate_title(title: str) -> str:
    if ' ' in title:
        title = '_'.join(title.split())

    if len(title) > 128:
        logger.critical(f'{title} превышает допустимую длину названия 128 < {len(title)}')
        raise ValueError(f'длина названия таблицы {len(title)} символа. максимально 128')
    return title

def validate_cols(cols: List[str]) -> List[str]:
    if len(cols) > 64:
        logger.critical(f'колличество стобцов ({len(cols)}) превышает 64')
        raise ValueError(f'максимальное количество столбцов 64')
    for index, col in enumerate(cols):
        if ' ' in col:
            col = '_'.join(col.split())
            cols[index] = col
        if len(col) > 128:
            logger.critical(f'длина названия столбца ({col, len(col)}) превышает 128')
            raise ValueError(f'длина названия столбца {len(col)} символа. максимально 128')
    return cols
        

class Table(BaseModel):
    '''
    сущность таблицы для бизнес-логики
    '''
    title: Annotated[str, AfterValidator(validate_title)]
    cols: Annotated[List[str], AfterValidator(validate_cols)]
    rows: List[List[str]]
    in_analytics: bool

    @model_validator(mode='after')
    def validate_rows_number(self) -> Self:
        for row in self.rows:
            if len(row) != len(self.cols):
                logger.critical(f'количество столбцов - {len(self.cols)} не совпадает с количеством значений в строке - {len(row)}')
                raise ValueError(f'количество столбцов - {len(self.cols)} не совпадает с количеством значений в строке - {len(row)}\n\n\ncols={self.cols}\n\n\nrow={row}')
        return self