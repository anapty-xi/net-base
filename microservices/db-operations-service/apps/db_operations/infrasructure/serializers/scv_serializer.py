from django.core.files.uploadedfile import UploadedFile

class CsvHandler:
    '''класс предосталяющий части таблицы для ее создания'''
    def __init__(self, file: UploadedFile):
        if not file.name.endswith('.csv'):
            raise TypeError
        self.file = file
    def table_title(self):
        return self.file.name.endswith('.csv')
    def cols(self):
        return self.file.file.readline().decode('utf-8-sig').strip().split(';')
    def rows(self):
        return self.file.file.read().decode('utf-8')