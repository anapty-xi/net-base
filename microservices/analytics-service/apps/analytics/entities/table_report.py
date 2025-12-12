from pydantic import BaseModel, model_validator
from typing import Self

class TableReport(BaseModel):
    '''
    Сущность для отчета о таблице

    all_rows: общее число строк
    checked: число проверенных строк
    success: число проверенных строк без замечаний
    remarks: число проверенных строк с замечаниями
    elemenated_remarks_today: число утсраненных замечаний сегодня
    remarks_today: число найденных замечаний сегодня
    checked_today: число проверенных строк сегодня
    rest: колличество непроверенных строк
    '''
    title: str
    all_rows: int
    checked: int
    success: int
    remarks: int
    elemenated_remarks_today: int
    remarks_today: int
    checked_today: int
    rest: int

    @model_validator(mode='after')
    def all_cheked_rest_validator(self) ->  Self:
        if self.all_rows < self.checked or self.all_rows < self.rest or self.all_rows - self.checked != self.rest:
            raise ValueError(f'Значения all_rows = {self.all_rows}, checked = {self.checked}, rest = {self.rest} противоречат друг другу')
        return self
    
    @model_validator(mode='after')
    def success_remarks_validator(self) -> Self:
        if self.success > self.checked or self.remarks > self.checked or self.success + self.remarks != self.checked:
            raise ValueError(f'Значения success = {self.success}, remarks = {self.remarks}, checked = {self.checked} противоречат друг другу')
        return self

    @model_validator(mode='after')
    def today_validator(self) -> Self:
        if self.checked_today > self.checked or self.remarks_today > self.checked_today:
            raise ValueError(f'Значения checked_today = {self.checked_today}, remarks = {self.remarks}, checked = {self.checked} противоречат друг другу')
        return self
    