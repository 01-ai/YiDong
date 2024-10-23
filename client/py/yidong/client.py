import mimetypes
import os
from datetime import datetime
from time import sleep
from typing import Iterable

import httpx
from jsonargparse import CLI
from yidong.config import CONFIG
from yidong.model import (
    Pagination,
    Reply,
    ResourceBase,
    ResourceUploadResponse,
    ResourceUrlResponse,
    Task,
    TaskContainer,
    TaskInfo,
    TaskResult,
)


class YiDong:
    _client: httpx.Client

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self._client = httpx.Client(
            base_url=base_url or CONFIG.base_url,
            headers={CONFIG.api_key_header: api_key or CONFIG.api_key},
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        payload: dict | None = None,
        headers: dict | None = None,
        content: str | bytes | Iterable[bytes] | None = None,
    ):
        resp = self._client.request(
            method=method,
            url=path,
            params=params,
            json=payload,
            headers=headers,
            content=content,
        )
        # TODO: handle err code
        reply = Reply.parse_obj(resp.json())
        return reply.data

    def add_resource(self, file: str, content_type: str | None = None) -> str:
        if os.path.exists(file):
            if content_type is None:
                content_type, _ = mimetypes.guess_type(file)
                if content_type is None:
                    raise Exception("Content type cant not be inferred")
            with open(file, "rb") as f:
                r = self._client.put(
                    f"/resource",
                    content=f,
                    headers={"Content-Type": content_type},
                    params={"file": file},
                )
                if r.status_code == 307:
                    f.seek(0)
                    r = self._client.put(
                        r.headers["Location"],
                        content=f,
                        headers={"Content-Type": content_type},
                    )
                res = ResourceUploadResponse.parse_obj(r.json())
                self.update_resource(res.id, name=os.path.basename(file))
                return res.id
        else:
            raise FileNotFoundError(f"File not found: {file}")

    def list_resource(self) -> Pagination[ResourceBase]:
        return Pagination[ResourceBase].parse_obj(self._request("get", "/resource"))

    def update_resource(self, rid: str, name: str | None = None):
        return self._request("patch", f"/resource/{rid}", payload={"name": name})

    def get_resource(self, rid: str) -> ResourceBase:
        return ResourceBase.parse_obj(self._request("get", f"/resource/{rid}"))

    def get_resource_url(self, rid: str, is_public: bool = True) -> str:
        return ResourceUrlResponse.parse_obj(
            self._request(
                "get", f"/resource/{rid}/url", params={"is_public": is_public}
            )
        ).url

    def delete_resource(self, rid: str) -> None:
        self._request("delete", f"/resource/{rid}")

    def submit_task(self, t: Task) -> str:
        return TaskInfo.parse_obj(self._request("post", "/task", payload=t.dict())).id

    def list_task(self) -> Pagination[TaskContainer]:
        return Pagination[TaskContainer].parse_obj(self._request("get", "/task"))

    def get_task(self, tid: str) -> TaskContainer:
        return TaskContainer.parse_obj(self._request("get", f"/task/{tid}"))

    def get_task_result(
        self, tid: str, poll_interval: float = 1.0, timeout: float = 0
    ) -> TaskResult:
        start = datetime.now()
        while True:
            t = self.get_task(tid)
            if t.records:
                print(
                    f"{tid}\t{t.records[-1].time}\t{t.records[-1].type}\t{t.records[-1].message}"
                )
            if t.result is not None:
                return t.result
            now = datetime.now()
            if timeout > 0 and (now - start).total_seconds() > timeout:
                raise TimeoutError(
                    f"failed to fetch task [{tid}] result within {timeout} seconds"
                )
            sleep(poll_interval)

    def delete_task(self, tid: str) -> bool:
        return self._request("delete", f"/task/{tid}")


def main():
    print(CLI(YiDong))


if __name__ == "__main__":
    main()
