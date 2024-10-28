# YiDong

> "The difficult thing isn't living with other people, it's understanding them."
> 
> -- José Saramago, Blindness

**YiDong** is designed to facilitate seamless interaction with the Yi series
multi-modal models, enabling users to perform a variety of tasks including image/video
comprehension, creation, and modification.

## Prerequisites

Make sure you have a valid API key.

⚠️: This project is still in the early test stage and is open to invited users only. Please contact yi@01.ai if you want to join the waitlist.

## Getting Started

We provide SDK in the following programming languages:

- Python

### Python

1. Install the `yidong` package:

    ```bash
    pip install yidong
    ```

2. Initialize the client

    ```py
    from yidong import YiDong

    yd = YiDong(api_key="YOUR_API_KEY")
    ```

    You can also set the `YIDONG_API_KEY` environment variable instead and left the `api_key` param empty.

3. Upload resources

    ```py
    rid = yd.add_resource("path/to/your/video.mp4")
    # "b525d791a0a5a023"
    ```

    A resource ID will be returned once the upload is completed. Then you can fetch the resource details:

    ```py
    yd.get_resource(rid)

    # Resource(
    #     id='b525d791a0a5a023',
    #     mime='video/mp4',
    #     name='a.mp4',
    #     source=ResourceFromLocalUpload(type='local_upload', path='~/Downloads/a.mp4'),
    #     uploaded_at='2024-10-25T18:23:13.021277',
    #     created_at='2024-10-25T18:23:14.204159',
    #     updated_at='2024-10-25T18:23:15.163147',
    #     url='https://...',
    #     meta={...}
    # )
    ```

4. Perform tasks

    ```py
    t = yd.video_summary('b525d791a0a5a023')
    # TaskRef("e5622d45e5ad41bfa961b09c0b84835b")
    ```

    A task reference will be returned immediately. To fetch the task result:

    ```py
    t()
    # VideoSummaryTaskResult(
    #     type='video_summary',
    #     video_id='e24bb328df3a5bb9',
    #     video_summary=Summary(
    #         summary='...',
    #         meta={}
    #     ),
    #     chapters=[Chapter(start=0.0, stop=10.0), Chapter(start=10.0, stop=13.0)],
    #     chapter_summaries=[
    #         Summary(
    #             summary='...',
    #             meta={}
    #         ),
    #         Summary(
    #             summary='...',
    #             meta={}
    #         )
    #     ]
    # )
    ```

    If you have a webhook set up, you will receive a notification once the task is completed. (TODO: verify this)

    You may find all available tasks in the docs(TODO: setup docs).

5. Live interaction

    (TODO: Add chat interface)

For more examples, please visit the [Gradio Example(TODO: Add Link)]().

#### CLI

You can also use the command line interface to perform tasks demonstrated above:

```bash
$ yidong -h

$ yidong add_resource ~/Downloads/a.mp4
# 'b525d791a0a5a023'

$ yidong video_summary b525d791a0a5a023
# TaskRef("e5622d45e5ad41bfa961b09c0b84835b")

$ yidong get_task e5622d45e5ad41bfa961b09c0b84835b
```
