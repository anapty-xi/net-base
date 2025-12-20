import pandas as pd
from typing import List
from io import BytesIO

class XLSXSerializer:
    '''
    преобразует столбцы и строки таблицы в xlxs в байтах
    '''
    def serialize(self, title: str, cols: List[str], rows: List[List[str]]): 
        table_df = pd.DataFrame(rows, columns=cols)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            table_df.to_excel(writer, sheet_name=title[:31], index=False)
        buffer.seek(0)
        return buffer.read()