import mimetypes
import os

import httpx
from yidong.config import CONFIG
from yidong.model import ResourceBase, ResourceUploadResponse, ResourceUrlResponse


class YiDong:
    _client: httpx.Client

    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        self._client = httpx.Client(
            base_url=base_url or CONFIG.base_url,
            headers={CONFIG.api_key_header: api_key or CONFIG.api_key},
        )

    def add_resource(self, file: str) -> str:
        if os.path.exists(file):
            content_type, _ = mimetypes.guess_type(file)
            if content_type is None:
                raise ValueError(f"Could not determine content type for file: {file}")
            with open(file, "rb") as f:
                r = self._client.put(
                    f"/resource",
                    content=f,
                    headers={"Content-Type": content_type},
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

    def list_resource(self) -> list[str]:
        resp = self._client.get("/resource")
        return resp.json()

    def update_resource(self, rid: str, name: str | None = None):
        self._client.patch(f"/resource/{rid}", json={"name": name})

    def get_resource(self, rid: str) -> ResourceBase:
        resp = self._client.get(f"/resource/{rid}")
        return ResourceBase.parse_obj(resp.json())

    def get_resource_url(self, rid: str, is_public: bool = True) -> str:
        resp = self._client.get(f"/resource/{rid}/url", params={"is_public": is_public})
        return ResourceUrlResponse.parse_obj(resp.json()).url

    def delete_resource(self, rid: str) -> None:
        self._client.delete(f"/resource/{rid}")
