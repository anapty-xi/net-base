import pandas as pd
from typing import List, Dict
from io import BytesIO
from django.core.files.uploadedfile import UploadedFile


class XLSXSerializer:
    '''
    преобразует столбцы и строки таблицы в xlxs в байтах
    '''
    def unserialize(self, file: UploadedFile) -> Dict[str, str | List[str] | List[List[str]]]:
        if not file.name.endswith('.xlsx'):
            raise TypeError('Файл должен быть в формате xlsx')
        xlxs_file = pd.read_excel(file.file)
        self.title = file.name.split('.')[0]
        self.cols = [str(col) for col in xlxs_file.columns.to_list()]
        self.rows = xlxs_file.to_numpy()

        str_rows = []
        for row in self.rows:
            str_row = []
            for cell in row:
                if pd.isna(cell):
                    str_row.append('')
                elif isinstance(cell, pd.Timestamp):
                    str_row.append(cell.strftime('%Y-%m-%d'))
                else:
                    str_row.append(str(cell))
            str_rows.append(str_row)
        
        return {
            'title': self.title,
            'cols': self.cols,
            'rows': str_rows
        }
            



    def serialize(self, title: str, cols: List[str], rows: List[List[str]]): 
        table_df = pd.DataFrame(rows, columns=cols)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            table_df.to_excel(writer, sheet_name=title[:31], index=False)
        buffer.seek(0)
        return buffer.read()