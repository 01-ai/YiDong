from enum import Enum, StrEnum
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


class WebhookResponse(BaseModel):
    user_id: str
    webhook_id: str
    url: str
    secret: str
    status: str
    created_at: str
    updated_at: str


#####


class PingTask(BaseModel):
    type: Literal["ping"] = "ping"


class PingTaskResult(BaseModel):
    type: Literal["ping"] = "ping"


class VideoGenerationTask(BaseModel):
    type: Literal["video_generation"] = "video_generation"
    image_id: str = ""
    prompt: str | None = None


class VideoGenerationTaskResult(BaseModel):
    type: Literal["video_generation"] = "video_generation"
    video_ids: list[str]


class VideoSummaryTask(BaseModel):
    type: Literal["video_summary"] = "video_summary"
    video_id: str
    prompt: str | None = None
    chapter_prompt: str | None = None
    chapters: list[Chapter] | None = None
    display_lang: str = "en"


class VideoSummaryTaskResult(BaseModel):
    type: Literal["video_summary"] = "video_summary"
    video_id: str
    video_summary: Summary | None
    chapters: list[Chapter]
    chapters_ids: list[str]
    chapter_summaries: list[Summary | None]


class VideoScriptTaskElement(BaseModel):
    video_id: str
    video_summary: Summary
    chapters_ids: list[str] | None = None
    chapters: list[Chapter]
    chapter_summaries: list[Summary]


class VideoScriptTaskResultElement(BaseModel):
    video_id: str
    chapter_id: str | None = None
    chapter: Chapter
    data: dict


class VideoScriptTask(BaseModel):
    type: Literal["video_script"] = "video_script"
    collection: list[VideoScriptTaskElement]
    remix_s1_prompt: str
    remix_s2_prompt: str
    references: list[list[VideoScriptTaskResultElement]] = []
    lang: str = "en"


class VideoScriptTaskResult(BaseModel):
    type: Literal["video_script"] = "video_script"
    styles: list[list[VideoScriptTaskResultElement]]


class BgmConfig(BaseModel):
    resource_id: str = ""
    volume: float = 0.0


class GlobalEditorConfig(BaseModel):
    bgm_config: BgmConfig = BgmConfig()
    output_width: float | None = None
    output_height: float | None = None


class AudioEditorConfig(BaseModel):
    resource_id: str = ""
    start: float = 0.0
    speed: float = 1.0
    volume: float = 25


class VoiceoverEditorConfig(BaseModel):
    text: str = ""
    font: str = ""
    font_size: int = 0
    font_color: str = ""
    font_weight: str = ""
    lang: str = ""
    position_x: float | None = None
    position_y: float | None = None
    style: str = "0"
    highlight_color: str = ""
    stroke_color: str = ""
    mask_type: str = "roll_mask"
    mask_color: str = "#800080"


class TextoverEditorConfig(BaseModel):
    text: str = ""
    font: str = ""
    font_size: int = 0
    font_color: str = ""
    font_weight: str = ""
    lang: str = ""
    position: str = "bottom"
    style: str = "0"
    max_lines: int = 3
    highlight_color: str = ""
    stroke_color: str = ""
    mask_color: str = ""
    effect_in: str = ""
    effect_out: str = ""
    effect_bubble: str = ""


class ImageEditorConfig(BaseModel):
    resource_id: str = ""
    start: float = 0.0
    stop: float = 0.0
    scale: float = 1.0
    position_x: float = 1.0
    position_y: float = 1.0
    rotate: float = 0.0
    animation: str = ""


class VideoEditorConfig(BaseModel):
    resource_id: str = ""
    position_x: float = 1.0
    position_y: float = 1.0
    rotate: float = 0.0
    animation: str = ""
    black_fill: str = "1"


class TransitionEditorConfig(BaseModel):
    style: str = ""
    duration: float = 0.5


class ChapterEditorConfig(BaseModel):
    key: str = ""
    audio: AudioEditorConfig = AudioEditorConfig()
    voiceover: VoiceoverEditorConfig = VoiceoverEditorConfig()
    textover: TextoverEditorConfig = TextoverEditorConfig()
    image: ImageEditorConfig = ImageEditorConfig()
    video: VideoEditorConfig = VideoEditorConfig()
    transition: TransitionEditorConfig = TransitionEditorConfig()


class EditorConfig(BaseModel):
    global_editor_config: GlobalEditorConfig = GlobalEditorConfig()
    chapter_editor_configs: list[ChapterEditorConfig] = []


class VideoMashupTask(BaseModel):
    type: Literal["video_mashup"] = "video_mashup"
    video_ids: list[str]
    chapters: list[Chapter] | None
    voice_overs: list[str]
    bgm_id: str
    voice_style_id: str
    voice_style_text: str
    lang: str = "en"
    editor_config: EditorConfig | None = None


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


class VideoSnapshotTask(BaseModel):
    type: Literal["video_snapshot"] = "video_snapshot"
    video_id: str
    start: float
    step: int
    stop: float


class VideoSnapshotTaskResult(BaseModel):
    type: Literal["video_snapshot"] = "video_snapshot"
    image_ids: list[str]


class DiffusionModel(StrEnum):
    SDXL = "sdxl"
    FLUX = "flux"


class DiffusionConfig(BaseModel):
    model: str = DiffusionModel.SDXL
    width: str = "1024"
    height: str = "1024"
    steps: int = 20
    count: int = 1


class ImageGenerationTask(BaseModel):
    type: Literal["image_generation"] = "image_generation"
    prompt: str = ""
    image_id: str = ""
    config: DiffusionConfig = DiffusionConfig()


class ImageGenerationTaskResult(BaseModel):
    type: Literal["image_generation"] = "image_generation"
    generated_image_ids: list[str]


class ImageInpaintTask(BaseModel):
    type: Literal["image_inpaint"] = "image_inpaint"
    image_id: str = Field(..., min_length=1)
    mask_base64: str = Field(..., min_length=1)
    prompt: str | None = None


class ImageInpaintTaskResult(BaseModel):
    type: Literal["image_inpaint"] = "image_inpaint"
    generated_image_ids: list[str]


class ImageRemoveTask(BaseModel):
    type: Literal["image_remove"] = "image_remove"
    image_id: str = Field(..., min_length=1)
    mask_base64: str = Field(..., min_length=1)


class ImageRemoveTaskResult(BaseModel):
    type: Literal["image_remove"] = "image_remove"
    generated_image_ids: list[str]


Task = Annotated[
    Union[
        PingTask,
        VideoGenerationTask,
        VideoSummaryTask,
        VideoScriptTask,
        VideoMashupTask,
        VideoConcatTask,
        VideoSnapshotTask,
        ImageGenerationTask,
        ImageInpaintTask,
        ImageRemoveTask,
    ],
    Field(discriminator="type"),
]

TaskType = TypeVar("TaskType", bound=Task)

TaskResult = Annotated[
    Union[
        PingTaskResult,
        VideoGenerationTaskResult,
        VideoSummaryTaskResult,
        VideoScriptTaskResult,
        VideoMashupTaskResult,
        VideoConcatTaskResult,
        VideoSnapshotTaskResult,
        ImageGenerationTaskResult,
        ImageInpaintTaskResult,
        ImageRemoveTaskResult,
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
