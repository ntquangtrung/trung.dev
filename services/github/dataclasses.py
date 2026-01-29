from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class RepositoriesParams:
    visibility: Optional[Literal["all", "public", "private"]] = None
    affiliation: Optional[str] = None
    type: Optional[Literal["all", "owner", "public", "private", "member"]] = "all"
    sort: Optional[Literal["created", "updated", "pushed", "full_name"]] = "full_name"
    direction: Optional[Literal["asc", "desc"]] = None
    per_page: Optional[int] = 30
    page: Optional[int] = 1

    def __post_init__(self):
        if self.type is not None and (
            self.visibility is not None or self.affiliation is not None
        ):
            raise ValueError(
                "`type` cannot be used together with `visibility` or `affiliation`"
            )
