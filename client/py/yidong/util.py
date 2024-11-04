from typing import Any, Callable, Generic, Iterable, Iterator, TypeVar

from yidong.model import Pagination, Resource, TaskContainer, TaskResultType, TaskType


class ResourceRef:
    def __init__(self, client: "YiDong", rid: str, **kwargs) -> None:
        self.client = client
        self.rid = rid
        self.meta = kwargs

    def __call__(self) -> Resource | None:
        return self.client.get_resource(self.rid)

    def __repr__(self) -> str:
        return f"ResourceRef('{self.rid}', {self.meta})"

    def __getitem__(self, key: str):
        return self.meta[key]


class TaskRef(Generic[TaskType, TaskResultType]):
    def __init__(self, client: "YiDong", tid: str) -> None:
        self.client = client
        self.tid = tid
        self.t: TaskContainer[TaskType, TaskResultType] | None = None

    def __call__(self, **kwargs) -> TaskResultType | None:
        if self.t is None or self.t.result is None:
            self.t = self.client.get_task(self.tid, **kwargs)
        return self.t.result

    def __getattr__(self, name: str) -> Any:
        if self.t is None:
            return None
        return getattr(self.t, name)

    def __repr__(self) -> str:
        if self.t is None:
            return f'TaskRef("{self.tid}")'
        else:
            return repr(self.t)


T = TypeVar("T")


class PaginationIter(Iterable[T], Generic[T]):
    def __init__(
        self, page_getter: Callable[[int], Pagination[T]], start_page: int = 1
    ) -> None:
        self.page_getter = page_getter
        self.page: Pagination[T] = page_getter(start_page)

        self.next_page = start_page + 1
        self.next_ele_index = 0

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        if self.next_ele_index < len(self.page.list):
            x = self.page.list[self.next_ele_index]
            self.next_ele_index += 1

            if self.next_ele_index >= len(self.page.list):
                self.page = self.page_getter(self.next_page)
                self.next_page += 1
                self.next_ele_index = 0
            return x
        else:
            raise StopIteration()
