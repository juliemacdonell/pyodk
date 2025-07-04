import logging
from dataclasses import dataclass
from datetime import datetime

from pyodk._endpoints.bases import Model, Service
from pyodk._utils import validators as pv
from pyodk._utils.session import Session
from pyodk.errors import PyODKError
from typing import Optional

log = logging.getLogger(__name__)


class EntityListProperty(Model):
    name: str
    odataName: str
    publishedAt: datetime
    forms: list[str]


@dataclass(frozen=True)
class URLs:
    post: str = "projects/{project_id}/datasets/{entity_list_name}/properties"


class EntityListPropertyService(Service):
    __slots__ = (
        "urls",
        "session",
        "default_project_id",
        "default_entity_list_name",
    )

    def __init__(
        self,
        session: Session,
        default_project_id: Optional[int] = None,
        default_entity_list_name: Optional[str] = None,
        urls: URLs = None,
    ):
        self.urls: URLs = urls if urls is not None else URLs()
        self.session: Session = session
        self.default_project_id: Optional[int] = default_project_id
        self.default_entity_list_name: Optional[str] = default_entity_list_name

    def create(
        self,
        name: str,
        entity_list_name: Optional[str] = None,
        project_id: Optional[int] = None,
    ) -> bool:
        """
        Create an Entity List Property.

        :param name: The name of the Property. Property names follow the same rules as
          form field names (valid XML identifiers) and cannot use the reserved names of
          name or label, or begin with the reserved prefix __.
        :param entity_list_name: The name of the Entity List (Dataset) being referenced.
        :param project_id: The id of the project this Entity List belongs to.
        """
        try:
            pid = pv.validate_project_id(project_id, self.default_project_id)
            eln = pv.validate_entity_list_name(
                entity_list_name, self.default_entity_list_name
            )
            req_data = {"name": pv.validate_str(name, key="name")}
        except PyODKError as err:
            log.error(err, exc_info=True)
            raise

        response = self.session.response_or_error(
            method="POST",
            url=self.session.urlformat(
                self.urls.post,
                project_id=pid,
                entity_list_name=eln,
            ),
            logger=log,
            json=req_data,
        )
        data = response.json()
        return data["success"]
