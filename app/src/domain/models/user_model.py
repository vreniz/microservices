from sqlmodel import Field, SQLModel
import datetime
import uuid

class User(SQLModel, table=True):  
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(index=True)
    email: str = Field(index=True)
    identification_type: str
    identification_number: str
    birth_date: datetime.date
    is_active: bool = True


    __tablename__ = "usr_users"