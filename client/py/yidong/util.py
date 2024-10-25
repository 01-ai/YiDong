from datetime import datetime
from time import sleep
from typing import Callable, Generic, TypeVar

from yidong.model import Pagination, TaskContainer, TaskResult


class TaskRef:
    def __init__(self, client: "YiDong", tid: str) -> None:
        self.client = client
        self.tid = tid
        self.t: TaskContainer | None = None

    def __call__(
        self, blocking: bool = True, poll_interval: float = 1.0, timeout: float = 0
    ) -> TaskResult | None:
        if self.t is None or self.t.result is None:
            if blocking:
                start = datetime.now()
                while True:
                    t = self.client.get_task(self.tid)
                    self.t = t
                    if t.result is not None:
                        return t.result
                    if t.records:
                        print(
                            f"{self.tid}\t{t.records[-1].time}\t{t.records[-1].type}\t{t.records[-1].message}"
                        )
                    now = datetime.now()
                    if timeout > 0 and (now - start).total_seconds() > timeout:
                        raise TimeoutError(
                            f"failed to fetch task [{self.tid}] result within {timeout} seconds"
                        )
                    sleep(poll_interval)
            else:
                t = self.client.get_task(self.tid)
                self.t = t
                return t.result
        else:
            return self.t.result

    @property
    def status(self) -> str:
        if self.t is None or self.t.result is None:
            t = self.client.get_task(self.tid)
            self.t = t

        return self.t.records[-1].type

    def __repr__(self) -> str:
        return f'TaskRef("{self.tid}")'


T = TypeVar("T")


class PaginationIter(Generic[T]):
    def __iter__(self, page_getter: Callable[[], Pagination[T]]):
        self.page_getter = page_getter
        self.page: Pagination[T] | None = None

        self.next_page_index = 0
        self.next_ele_index = 0
        return self

    def __next__(self) -> T:
        if self.page is None:
            self.page = self.page_getter()

        n = self.next_page_index * self.page.page_size + self.next_ele_index
        if n < self.page.total:
            x = self.page.list[self.next_ele_index]
            self.next_ele_index += 1
            if self.next_ele_index >= self.page.page_size:
                self.next_ele_index = 0
                self.next_page_index += 1
            return x
        else:
            raise StopIteration()
