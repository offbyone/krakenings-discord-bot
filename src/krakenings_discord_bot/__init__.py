from dataclasses import dataclass

from svcs import Container, Registry

REGISTRY = Registry()


@dataclass
class ContainerHolder:
    container: Container | None = None


__CONTAINER_HOLDER = ContainerHolder()


def init(registry=REGISTRY):
    __CONTAINER_HOLDER.container = Container(registry)


def svcs_from() -> Container:
    assert __CONTAINER_HOLDER.container is not None
    return __CONTAINER_HOLDER.container
