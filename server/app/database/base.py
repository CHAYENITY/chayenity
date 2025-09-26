from sqlmodel import SQLModel


# Provide a `Base` object that exposes the SQLModel metadata so tests and
# other database utilities that call `Base.metadata.create_all()` will
# create the tables defined with SQLModel. SQLModel already maintains a
# `metadata` object; we simply reference it here for compatibility.
class Base:
    metadata = SQLModel.metadata
