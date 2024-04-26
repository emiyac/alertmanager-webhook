from typing import Dict, List, Union

from pydantic import BaseModel


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


class ResponseModel(BaseModel):
    code: str
    msg: str
    data: object = None
