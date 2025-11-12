from pydantic import BaseModel
from typing import Optional
from schemas.userDetail import UserDetailOut
from typing import List

class InputUser(BaseModel):
    username: str
    password: str

class InputLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    userdetail: Optional[UserDetailOut] = None

    class Config:
        from_attributes = True
        
class PaginatedFilteredBody(BaseModel):
    """Cuerpo que recibe el endpoint de usuarios paginados"""
    limit: Optional[int] = 20
    last_seen_id: Optional[int] = 0
    search: Optional[str] = None


class PaginatedUsersOut(BaseModel):
    """Respuesta del endpoint paginado de usuarios"""
    users: List[UserOut]
    next_cursor: Optional[int] = None

    class Config:
        from_attributes = True