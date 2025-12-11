from pydantic import BaseModel, model_validator
from typing import Self

class TableReport(BaseModel):
    title: str
    all_rows: int
    cheked: int
    success: int
    remarks: int
    elemenated_remarks_today: int
    remarks_today: int
    cheked_today: int
    rest: int

    @model_validator(mode='after')
    def all_cheked_rest_validator(self) ->  Self:
        if self.all_rows < self.cheked or self.all_rows > self.rest or self.all_rows - self.cheked != self.rest:
            raise ValueError(f'Значения all_rows = {self.all_rows}, checked = {self.cheked}, rest = {self.rest} противоречат друг другу')
        return self
    
    @model_validator(mode='after')
    def success_remarks_validator(self) -> Self:
        if self.success > self.cheked or self.remarks > self.cheked or self.success + self.remarks != self.cheked:
            raise ValueError(f'Значения success = {self.success}, remarks = {self.remarks}, cheked = {self.cheked} противоречат друг другу')
        return self

    @model_validator(mode='after')
    def today_validator(self) -> Self:
        if self.cheked_today > self.cheked or self.remarks_today > self.cheked_today:
            raise ValueError(f'Значения checked_today = {self.cheked_today}, remarks = {self.remarks}, cheked = {self.cheked} противоречат друг другу')
        return Self
    