from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    is_active: bool
    is_staff: bool     
    id: Optional[int] = None
    username: str = ''
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
   

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False

    def make_staff(self) -> None:
        self.is_staff = True

    def remove_staff(self) -> None:
        self.is_staff = False
