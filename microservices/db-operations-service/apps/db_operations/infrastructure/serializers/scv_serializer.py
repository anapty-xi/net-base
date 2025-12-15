from django.core.files.uploadedfile import UploadedFile

class CsvHandler:
    '''
    Обработка файла в соответствии с структурой таблицы 
    '''
    def __init__(self, file: UploadedFile):
        if not file.name.endswith('.csv'):
            raise TypeError
        self.file = file

        self.table_title = self.file.name.split('.csv')[0]
        self.cols = self.file.file.readline().decode('utf-8-sig').strip().split(';')
        self.rows =  [row.split(';') for row in self.file.file.read().decode('utf-8').split('\n')][0:-1]