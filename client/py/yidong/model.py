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
    meta: dict | None
    url: str

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

    def __getitem__(self, i: int) -> T:
        return self.list[i]

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self) -> T:
        if self._i < len(self.list):
            x = self.list[self._i]
            self._i += 1
            return x
        else:
            raise StopIteration()


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
    chapters_ids: list[str]
    chapter_summaries: list[Summary | None]


class GenScriptElement(BaseModel):
    video_id: str
    video_summary: Summary
    chapters: list[Chapter]
    chapter_summaries: list[Summary]


class GenScriptTask(BaseModel):
    type: Literal["video_script"] = "video_script"
    collection: list[GenScriptElement]
    remix_s1_prompt: str
    remix_s2_prompt: str


class GenScriptTaskResultElement(BaseModel):
    video_id: str
    chapter: Chapter
    data: dict


class GenScriptTaskResult(BaseModel):
    type: Literal["video_script"] = "video_script"
    styles: list[list[GenScriptTaskResultElement]]


class VideoMashupTask(BaseModel):
    type: Literal["video_mashup"] = "video_mashup"
    video_ids: list[str]
    chapters: list[Chapter] | None
    voice_overs: list[str]
    bgm_id: str
    voice_style_id: str


class VideoMashupTaskResult(BaseModel):
    type: Literal["video_mashup"] = "video_mashup"
    video_id: str
    raw_video_id: str
    voice_over_ids: list[str]
    bgm_id: str
    chapter_ids: list[str]


class VideoConcatTask(BaseModel):
    type: Literal["video_concat"] = "video_concat"
    video_ids: list[str]
    chapters: list[Chapter] = []


class VideoConcatTaskResult(BaseModel):
    type: Literal["video_concat"] = "video_concat"
    video_id: str


Task = Annotated[
    Union[PingTask, VideoSummaryTask, GenScriptTask, VideoMashupTask, VideoConcatTask],
    Field(discriminator="type"),
]

TaskType = TypeVar("TaskType", bound=Task)

TaskResult = Annotated[
    Union[
        PingTaskResult,
        VideoSummaryTaskResult,
        GenScriptTaskResult,
        VideoMashupTaskResult,
        VideoConcatTaskResult,
    ],
    Field(discriminator="type"),
]

TaskResultType = TypeVar("TaskResultType", bound=TaskResult)


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


class TaskContainer(BaseModel, Generic[TaskType, TaskResultType]):
    id: str
    task: TaskType
    result: TaskResultType | None
    records: list[TaskRecord]

    def is_done(self) -> bool:
        if self.records:
            return (
                self.records[-1].type == TaskRecordType.success
                or self.records[-1].type == TaskRecordType.fail
            )
        return False
