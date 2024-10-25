import mimetypes
import os
from typing import Iterable

import httpx
import rich
from jsonargparse import CLI
from pydantic import ValidationError
from yidong.config import CONFIG
from yidong.exception import YDError
from yidong.model import (
    Pagination,
    Reply,
    Resource,
    ResourceUploadResponse,
    T,
    Task,
    TaskContainer,
    TaskInfo,
)
from yidong.util import TaskRef


class YiDong:
    _client: httpx.Client

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self._client = httpx.Client(
            base_url=base_url or CONFIG.base_url,
            headers={CONFIG.api_key_header: api_key or CONFIG.api_key},
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
        resp = self._client.request(
            method=method,
            url=path,
            params=params,
            json=payload,
            headers=headers,
            content=content,
        )
        try:
            payload = resp.json()
            reply = Reply[T].parse_obj(payload)
        except ValidationError as e:
            raise YDError(1, str(e), payload)

        if reply.code != 0:
            raise YDError(reply.code, reply.message, reply.data)
        return reply.data

    def add_resource(self, file: str, content_type: str | None = None) -> Resource:
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
                res = Reply[ResourceUploadResponse].parse_obj(r.json())
                self.update_resource(res.data.id, name=os.path.basename(file))
                return self.get_resource(res.data.id)
        else:
            raise FileNotFoundError(f"File not found: {file}")

    def list_resource(self) -> Pagination[Resource]:
        return self._request(Pagination[Resource], "get", "/resource")

    def update_resource(self, rid: str, name: str | None = None) -> Resource:
        return self._request(
            Resource, "patch", f"/resource/{rid}", payload={"name": name}
        )

    def get_resource(self, rid: str) -> Resource:
        return self._request(Resource, "get", f"/resource/{rid}")

    def delete_resource(self, rid: str) -> None:
        self._request(bool, "delete", f"/resource/{rid}")

    def submit_task(self, t: Task) -> TaskRef:
        tid = self._request(TaskInfo, "post", "/task", payload=t.dict()).id
        return TaskRef(self, tid)

    def list_task(self) -> Pagination[TaskContainer]:
        return self._request(Pagination[TaskContainer], "get", "/task")

    def get_task(self, tid: str) -> TaskContainer:
        return self._request(TaskContainer, "get", f"/task/{tid}")

    def delete_task(self, tid: str) -> bool:
        return self._request(bool, "delete", f"/task/{tid}")


def main():
    rich.print(CLI(YiDong))


if __name__ == "__main__":
    main()
