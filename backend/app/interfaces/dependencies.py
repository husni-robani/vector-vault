from typing import Annotated

from fastapi import Depends, Request

from app.dependencies import Container


def _container(request: Request) -> Container:
    return request.app.state.container


ContainerDep = Annotated[Container, Depends(_container)]
