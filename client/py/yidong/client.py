import inspect
import mimetypes
import os
from datetime import datetime
from time import sleep
from typing import Any, Iterable, get_args
from urllib.parse import urlparse

import httpx
import rich
from jsonargparse import CLI
from pydantic import TypeAdapter, ValidationError
from yidong.config import CONFIG
from yidong.exception import (
    YDError,
    YDInternalServerError,
    YDInvalidReplyError,
    convert_reply_to_error,
)
from yidong.model import (
    Chapter,
    DiffusionConfig,
    EditorConfig,
    ImageGenerationTask,
    ImageGenerationTaskResult,
    ImageInpaintTask,
    ImageInpaintTaskResult,
    ImageRemoveTask,
    ImageRemoveTaskResult,
    Pagination,
    PingTask,
    PingTaskResult,
    Reply,
    Resource,
    ResourceUploadResponse,
    T,
    Task,
    TaskContainer,
    TaskInfo,
    VideoConcatTask,
    VideoConcatTaskResult,
    VideoGenerationTask,
    VideoGenerationTaskResult,
    VideoMashupTask,
    VideoMashupTaskResult,
    VideoScriptTask,
    VideoScriptTaskElement,
    VideoScriptTaskResult,
    VideoScriptTaskResultElement,
    VideoSnapshotTask,
    VideoSnapshotTaskResult,
    VideoSummaryTask,
    VideoSummaryTaskResult,
    WebhookResponse,
)
from yidong.util import PaginationIter, ResourceRef, TaskRef


class YiDong:
    _client: httpx.Client

    def __init__(
        self, api_key: str = CONFIG.api_key, base_url: str = CONFIG.base_url
    ) -> None:
        """Initialize the Client

        Args:
            base_url: The base url of the server.
            api_key: The api key for authentication.
        """
        self._client = httpx.Client(
            base_url=base_url, headers={CONFIG.api_key_header: api_key}
        )

    def _request(
        self,
        T: type[T],
        method: str,
        path: str,
        *,
        params: dict | None = None,
        payload: dict | None = None,
        headers: dict | None = None,
        content: str | bytes | Iterable[bytes] | None = None,
    ) -> T:
        try:
            resp = self._client.request(
                method=method,
                url=path,
                params=params,
                json=payload,
                headers=headers,
                content=content,
            )
            resp.raise_for_status()
            reply = Reply[T].parse_raw(resp.content)
        except httpx.HTTPStatusError as e:
            raise YDInternalServerError(e.response.status_code, e.response.text)
        except ValidationError:
            try:
                reply = Reply[Any].parse_raw(resp.content)
                raise convert_reply_to_error(reply)
            except ValidationError:
                raise YDInvalidReplyError(resp.content)

        return reply.data

    def add_resource(
        self, file: str | None = None, content_type: str | None = None
    ) -> Resource | ResourceRef:
        """Add a resource to the server. A resource id will be returned.

        Args:
            file: It can be either a local file path or a URL. If nothing is
                provided, a pre-signed url will be generated which you can use
                to upload the file later with the HTTP `PUT` request. Note that
                the `Content-Type` header should be set the same as the
                `content_type` parameter when uploading. Even if you do not
                provide the `content_type` parameter here, you should still set
                the `Content-Type` header as the default value of `content_type`
                of `application/octet-stream`.
            content_type: The mime content type of the file. If not provided, it
                will first try to guess the content type from the file
                extension. If it fails, it will be set to
                `application/octet-stream` by default. You can still update it
                later with the `update_resource` method.
        """
        if file is None:
            r = self._client.put(
                f"/resource",
                headers={"Content-Type": content_type or "application/octet-stream"},
            )
            if r.status_code == 307:
                return ResourceRef(
                    self,
                    r.headers["x-yds-resource-id"],
                    upload_url=r.headers["Location"],
                )
            else:
                raise YDError(1, "Failed to get pre-signed url", r.text)
        elif os.path.exists(file):
            headers = {
                "Content-Type": content_type
                or mimetypes.guess_type(file)[0]
                or "application/octet-stream"
            }
            r = self._client.put(
                f"/resource",
                headers=headers,
                params={"file": file},
            )
            if r.status_code == 307:
                rid = r.headers["x-yds-resource-id"]
                url = r.headers["Location"]
                with open(file, "rb") as f:
                    r = self._client.put(
                        url,
                        content=f,
                        headers=headers,
                    )
                return self.get_resource(rid)
            else:
                raise YDError(1, "Failed to get pre-signed url", r.text)
        else:
            o = urlparse(file)
            if o.scheme in ["http", "https"]:
                r = self._request(
                    ResourceUploadResponse, "put", f"/resource", params={"file": file}
                )
                return ResourceRef(self, r.id)
            else:
                raise FileNotFoundError(f"File not found: {file}")

    def update_resource(
        self, id: str, name: str | None = None, mime: str | None = None
    ) -> Resource:
        """Update the resource with the given id.

        Args:
            id: The resource id.
            name: The file name of the resource.
            mime: The mime content type of the resource.
        """
        return self._request(
            Resource, "patch", f"/resource/{id}", payload={"name": name, "mime": mime}
        )

    def list_resource(
        self,
        page: int = 1,
        page_size: int = 10,
        source: list[str] = ["local_upload", "remote_download"],
        ids: list[str] | None = None,
    ) -> Pagination[Resource]:
        """Retrieve resources in `page` based on filters of `source`. See also `list_resource_iter`.

        Args:
            page: The page number, starting from 1.
            page_size: The number of resources per page.
            source: The source of the resources.
        """
        params = {"page": page, "page_size": page_size, "source": source}
        if ids:
            params["ids"] = ids
        return self._request(
            Pagination[Resource],
            "get",
            "/resource",
            params=params,
        )

    def list_resource_iter(self, **kwargs) -> PaginationIter[Resource]:
        return PaginationIter[Resource](lambda p: self.list_resource(page=p, **kwargs))

    def get_resource(self, id: str) -> Resource:
        return self._request(Resource, "get", f"/resource/{id}")

    def download_resource(self, id: str, path: str | None = None) -> str:
        r = self.get_resource(id)
        path = path or r.name or f"{r.id}.{r.mime.split('/')[1]}"
        with open(path, "wb") as f:
            resp = httpx.get(r.url)
            f.write(resp.content)
        return path

    def delete_resource(self, id: str) -> None:
        self._request(bool, "delete", f"/resource/{id}")

    #####
    def list_webhook(self) -> list[WebhookResponse]:
        webhooks = self._request(Pagination[WebhookResponse], "get", "/webhook")
        return webhooks.list

    # TODO: add scope?
    def add_webhook(self, url: str, secret: str) -> WebhookResponse:
        return self._request(
            WebhookResponse, "post", "/webhook", payload={"url": url, "secret": secret}
        )

    def enable_webhook(self, webhook_id: str) -> WebhookResponse:
        return self._request(
            WebhookResponse,
            "patch",
            f"/webhook/{webhook_id}",
            payload={"status": "active"},
        )

    def disable_webhook(self, webhook_id: str) -> WebhookResponse:
        return self._request(
            WebhookResponse,
            "patch",
            f"/webhook/{webhook_id}",
            payload={"status": "inactive"},
        )

    def update_webhook(
        self, webhook_id: str, *, url: str | None = None, secret: str | None = None
    ) -> WebhookResponse:
        payload = {}
        if url is not None:
            payload["url"] = url
        if secret is not None:
            payload["secret"] = secret
        return self._request(
            WebhookResponse, "patch", f"/webhook/{webhook_id}", payload=payload
        )

    #####

    def list_task(
        self,
        page: int = 1,
        page_size: int = 10,
        ids: list[str] | None = None,
    ) -> Pagination[TaskContainer]:
        params = {"page": page, "page_size": page_size}
        if ids:
            params["ids"] = ids
        return self._request(Pagination[TaskContainer], "get", "/task", params=params)

    def list_task_iter(self, **kwargs) -> PaginationIter[TaskContainer]:
        return PaginationIter[TaskContainer](lambda p: self.list_task(page=p, **kwargs))

    def _get_task(self, id: str) -> TaskContainer:
        return self._request(TaskContainer, "get", f"/task/{id}")

    def get_task(
        self,
        id: str,
        block: bool = True,
        poll_interval: float = 1.0,
        timeout: float = 0,
    ) -> TaskContainer:
        """Get the task detail with the given task id.

        Args:
            id: The task id. block: Whether to block the request until the task is completed.
            poll_interval: The interval to poll the task status.
            timeout: The maximum time to wait for the task to finish. By default it will wait infinitely.
        """
        if block:
            start = datetime.now()
            while True:
                t = self._get_task(id)
                if t.is_done():
                    return t
                else:
                    if t.records:
                        print(
                            f"{id}\t{t.records[-1].time}\t{t.records[-1].type.value}\t{t.records[-1].message}"
                        )
                now = datetime.now()
                if timeout > 0 and (now - start).total_seconds() > timeout:
                    raise TimeoutError(
                        f"failed to fetch task [{id}] result within {timeout} seconds"
                    )
                sleep(poll_interval)
        else:
            return self._get_task(id)

    def delete_task(self, tid: str) -> bool:
        return self._request(bool, "delete", f"/task/{tid}")

    def _submit_task(self, payload: dict) -> TaskRef:
        caller = inspect.currentframe().f_back.f_code.co_name
        task_type, task_result_type = get_args(
            inspect.signature(getattr(self, caller)).return_annotation
        )
        payload = payload | {"type": caller}
        res = self._request(
            TaskInfo,
            "post",
            "/task",
            payload=TypeAdapter(Task).validate_python(payload).dict(),
        )
        return TaskRef[task_type, task_result_type](self, res.id)

    def image_generation(
        self,
        prompt: str = "",
        image_id: str = "",
        config: DiffusionConfig = DiffusionConfig(),
    ) -> TaskRef[ImageGenerationTask, ImageGenerationTaskResult]:
        """Generate images based on the given prompt or the reference image."""
        return self._submit_task(locals())

    def image_inpaint(
        self,
        image_id: str,
        mask_base64: str,
        prompt: str | None = None,
    ) -> TaskRef[ImageInpaintTask, ImageInpaintTaskResult]:
        """Image inpaint based on the mask image base64 string and the given prompt."""
        return self._submit_task(locals())

    def image_remove(
        self,
        image_id: str,
        mask_base64: str,
    ) -> TaskRef[ImageRemoveTask, ImageRemoveTaskResult]:
        """Image remove based on the mask image base64 string."""
        return self._submit_task(locals())

    def ping(self) -> TaskRef[PingTask, PingTaskResult]:
        """A simple task to test the health of the server."""
        return self._submit_task(locals())

    def video_concat(
        self, video_ids: list[str], chapters: list[Chapter] = []
    ) -> TaskRef[VideoConcatTask, VideoConcatTaskResult]:
        """Concatenate multiple videos into one. If `chapters` are provided, they should be of the same length as `video_ids`."""
        return self._submit_task(locals())

    def video_mashup(
        self,
        video_ids: list[str],
        voice_overs: list[str],
        bgm_id: str,
        voice_style_id: str,
        voice_style_text: str,
        chapters: list[Chapter] | None = None,
        lang: str = "en",
        editor_config: EditorConfig | None = None,
    ) -> TaskRef[VideoMashupTask, VideoMashupTaskResult]:
        """Create a new video based on the given videos and other elements.

        Args:
            video_ids: The list of video ids.
            chapters: The list of chapters. If not provided, the whole video will be used.
            voice_overs: The list of voice over texts.
            bgm_id: The background music id. Make sure it exists first.
            voice_style_id: The voice style resource id. Make sure it exists first by uploading your voice sample.
            voice_style_text: The transcript of the voice style.
            lang: The language of the voice over text. We'll choose appropriate font and style based on the language. Make sure the voice style matches the language specified here.
        """
        return self._submit_task(locals())

    def video_generation(
        self,
        prompt: str | None = None,
        image_id: str = "",
    ) -> TaskRef[VideoGenerationTask, VideoGenerationTaskResult]:
        """Generate video based on the given prompt and the reference image."""
        return self._submit_task(locals())

    def video_script(
        self,
        collection: list[VideoScriptTaskElement],
        remix_s1_prompt: str,
        remix_s2_prompt: str,
        references: list[list[VideoScriptTaskResultElement]],
        lang: str = "en",
    ) -> TaskRef[VideoScriptTask, VideoScriptTaskResult]:
        """
        Generate scripts based on a collection of video summarizations.
        """
        return self._submit_task(locals())

    def video_snapshot(
        self, video_id: str, *, start: float = 0.0, step: int = 1, stop: float = 0.0
    ) -> TaskRef[VideoSnapshotTask, VideoSnapshotTaskResult]:
        """Take snapshots of the video at the given timestamps.

        Args:
            video_id: The video id.
            start: The start timestamp in seconds.
            step: The step between each snapshot. (Only integers are allowed for now)
            stop: The stop timestamp in seconds. If it is longer than the video duration, only the video duration will be used.
        """
        return self._submit_task(locals())

    def video_summary(
        self,
        video_id: str,
        prompt: str | None = None,
        chapter_prompt: str | None = None,
        chapters: list[Chapter] | None = None,
        display_lang: str = "en",
    ) -> TaskRef[VideoSummaryTask, VideoSummaryTaskResult]:
        """
        Summarize a video with the given video id. By default, the video will be
        split into chapters. The summary of each chapter together with the summary of the whole video will be returned.

        Args:
            video_id: The video id.
            prompt: The prompt for the video summary. If not set, a builtin prompt will be used here.
            chapter_prompt: The prompt for the chapter summary. If not set, it will be the same as `prompt`.
            chapters: The list of video chapters. If not set, the `chapters` will be extracted automatically.
            display_lang: The language for selling_points, product name and so on
        """
        return self._submit_task(locals())


def main():
    rich.print(CLI(YiDong))


if __name__ == "__main__":
    main()
