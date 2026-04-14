  
from typing import Any
from uuid import UUID

from pydantic import BaseModel, model_validator

from api.src.utilities.utilities import is_float, is_uuid


class ChatroomCache(BaseModel):
    uid: str | UUID
    name: str
    about: str
    members_count: str | int
    room_type: str
    created_at: str | float
    modified_at: str | float
    creator_uid: str | UUID | None = None
    creator_successor_uid: str | UUID | None = None
    original_creator_username: str | None = None
    password: str | None = None
    
    @model_validator(mode="before")
    def check_value_type_are_valid(cls, data: Any):
        if isinstance(data, dict):
            uid_is_valid = is_uuid(uuid_str=data.get("uid"))
            created_at_is_valid = is_float(data.get("created_at"))
            modified_at_is_valid = is_float(data.get("modified_at"))
            
            if not uid_is_valid:
                raise Exception("chatroom cache uid value is not a valid uid.")
            
            if not str(data.get("members_count")).isnumeric():
                raise Exception("chatroom cache members_count value is not a valid integer.")
            if not created_at_is_valid:
                raise Exception("chatroom cache created_at value is not a valid float.")
            if not modified_at_is_valid:
                raise Exception("chatroom cache modified_at value is not a valid float.")

            creator_uid = data.get("creator_uid")
            if creator_uid:
                creator_uid_is_valid = is_uuid(uuid_str=creator_uid)
                if not creator_uid_is_valid:
                    raise Exception("chatroom cache creator_uid value is not a valid uid.")

            creator_successor_uid = data.get("creator_successor_uid")
            if creator_successor_uid:
                creator_successor_uid_is_valid = is_uuid(uuid_str=creator_successor_uid)
                if not creator_successor_uid_is_valid:
                    raise Exception("chatroom cache creator_successor_uid value is not a valid uid.")
                
        return data
            
    @model_validator(mode="after")
    def modify_fields(self):
        self.uid = UUID(self.uid)
        if self.creator_uid:
            self.creator_uid = UUID(self.creator_uid)
        if self.creator_successor_uid:
            self.creator_successor_uid = UUID(self.creator_successor_uid)
        
        self.members_count = int(self.members_count)
        self.created_at = float(self.created_at)
        self.modified_at = float(self.modified_at)
        
        return self
