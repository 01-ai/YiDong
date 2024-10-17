from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class ResourceUploadResponse(BaseModel):
    id: str


class ResourceBase(BaseModel):
    id: str
    mime: str
    name: str = ""
    uploaded_at: str
    created_at: str | None = None
    updated_at: str | None = None
    meta: dict | None = None


class ResourceUrlResponse(BaseModel):
    url: str


#####


class TaskInfo(BaseModel):
    id: str


class PingTask(BaseModel):
    type: Literal["ping"] = "ping"


class VideoSummaryTask(BaseModel):
    type: Literal["ping"] = "ping"
    video_id: str


Task = Annotated[
    Union[PingTask, VideoSummaryTask],
    Field(discriminator="type"),
]


#####


class PingTaskResult(BaseModel):
    type: str = "ping"


class VideoSummaryTaskResult(BaseModel):
    type: str = "ping"


TaskResult = Annotated[
    Union[
        PingTaskResult,
        VideoSummaryTaskResult,
    ],
    Field(discriminator="type"),
]


#####
class TaskRecordType(str, Enum):
    created = "created"
    submitted = "submitted"
    pending = "pending"
    processing = "processing"
    success = "success"
    fail = "fail"


class TaskRecord(BaseModel):
    message: str = ""
    type: TaskRecordType
    time: str


class TaskContainer(BaseModel):
    id: str
    task: Task
    result: TaskResult | None = None
    records: list[TaskRecord] = []
