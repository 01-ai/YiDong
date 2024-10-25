from enum import Enum
from typing import Annotated, Generic, Literal, TypeVar, Union

from pydantic import BaseModel, Field

T = TypeVar("T")


class ResourceUploadResponse(BaseModel):
    id: str


class ResourceFromLocalUpload(BaseModel):
    type: Literal["local_upload"] = "local_upload"
    path: str | None = None


class ResourceFromRemoteDownload(BaseModel):
    type: Literal["remote_download"] = "remote_download"
    url: str


class ResourceFromTask(BaseModel):
    type: Literal["task"] = "task"
    task_id: str


ResourceSource = Annotated[
    Union[
        ResourceFromLocalUpload,
        ResourceFromRemoteDownload,
        ResourceFromTask,
    ],
    Field(discriminator="type"),
]


class Resource(BaseModel):
    id: str
    mime: str
    name: str
    source: ResourceSource
    uploaded_at: str
    created_at: str | None
    updated_at: str | None
    meta: dict | None = Field(repr=False)

    def __getitem__(self, key):
        if self.meta:
            return self.meta[key]
        else:
            raise KeyError(key)


class ResourceUrlResponse(BaseModel):
    url: str


class Reply(BaseModel, Generic[T]):
    code: int
    message: str
    data: T


class TaskInfo(BaseModel):
    id: str


class Pagination(BaseModel, Generic[T]):
    page: int
    page_size: int
    total: int
    list: list[T]

    def __iter__(self):
        return self.list

    def __getitem__(self, i) -> T:
        return self.list[i]


class Chapter(BaseModel):
    start: float
    stop: float


class Summary(BaseModel):
    summary: str
    meta: dict = {}


#####


class PingTask(BaseModel):
    type: Literal["ping"] = "ping"


class PingTaskResult(BaseModel):
    type: Literal["ping"] = "ping"


class VideoSummaryTask(BaseModel):
    type: Literal["video_summary"] = "video_summary"
    video_id: str
    prompt: str | None = None
    chapter_prompt: str | None = None
    chapters: list[Chapter] | None = None


class VideoSummaryTaskResult(BaseModel):
    type: Literal["video_summary"] = "video_summary"
    video_id: str
    video_summary: Summary | None
    chapters: list[Chapter]
    chapter_summaries: list[Summary | None]


class GenScriptElement(BaseModel):
    video_id: str
    video_summary: Summary
    chapters: list[Chapter]
    chapter_summaries: list[Summary]


class GenScriptTask(BaseModel):
    type: Literal["gen_script"] = "gen_script"
    collection: list[GenScriptElement]
    remix_s1_prompt: str
    remix_s2_prompt: str


class GenScriptTaskResultElement(BaseModel):
    video_id: str
    chapter: Chapter
    data: dict


class GenScriptTaskResult(BaseModel):
    type: Literal["gen_script"] = "gen_script"
    styles: list[list[GenScriptTaskResultElement]]


class VideoMashupTask(BaseModel):
    type: Literal["video_mashup"] = "video_mashup"
    video_ids: list[str]
    chapters: list[Chapter]
    voice_overs: list[str]
    bgm_id: str
    voice_style_id: str


class VideoMashupTaskResult(BaseModel):
    type: Literal["video_mashup"] = "video_mashup"
    video_id: str


Task = Annotated[
    Union[PingTask, VideoSummaryTask, GenScriptTask, VideoMashupTask],
    Field(discriminator="type"),
]

TaskResult = Annotated[
    Union[
        PingTaskResult,
        VideoSummaryTaskResult,
        GenScriptTaskResult,
        VideoMashupTaskResult,
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

    def __repr__(self):
        return self.value


class TaskRecord(BaseModel):
    time: str
    type: TaskRecordType
    message: str = ""


class TaskContainer(BaseModel):
    id: str
    task: Task
    result: TaskResult | None
    records: list[TaskRecord]
