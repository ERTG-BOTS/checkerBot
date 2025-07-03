"""Import all routers and add them to routers_list."""
from .kpi import kpi_router
from .status import status_router

routers_list = [
    status_router,
    kpi_router,
]

__all__ = [
    "routers_list",
]
