from pydantic import BaseModel
from typing import List, Dict, Union


class AlertModel(BaseModel):
    status: str = None
    labels: Dict[str, Union[int, str]] = {}
    annotations: Dict[str, Union[int, str]] = {}
    startsAt: str = None
    endsAt: str = None
    generatorURL: str = None
    fingerprint: str = None


class AlertManagerModel(BaseModel):
    receiver: str = None
    status: str = None
    alerts: List[AlertModel] = []
    groupLabels: Dict[str, Union[int, str]] = {}
    commonLabels: Dict[str, Union[int, str]] = {}
    commonAnnotations: Dict[str, Union[int, str]] = {}
    externalURL: str = None
    truncatedAlerts: int = 0
