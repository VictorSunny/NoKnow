from uuid import UUID
from pydantic import BaseModel


class DictListUIDMatchResult(BaseModel):
    exists: bool
    occurences: int


class UIDObj:
    uid: UUID


def check_dict_list_for_uid_match(
    target_uid: UUID, dict_list: UIDObj
) -> DictListUIDMatchResult:
    target_exists = False
    occurences = 0
    for dict_obj in dict_list:
        if target_uid == dict_obj.get("uid"):
            target_exists = True
            occurences += 1
    result = DictListUIDMatchResult(exists=target_exists, occurences=occurences)
    return result
