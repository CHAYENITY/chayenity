from pydantic import BaseModel


class UpsertOut(BaseModel):
    success: bool


class CreateOut(UpsertOut):
    pass


class UpdateOut(UpsertOut):
    pass


class DeleteOut(UpsertOut):
    pass
