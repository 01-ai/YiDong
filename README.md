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
    r = yd.add_resource("path/to/your/video.mp4")
    ```

    A resource ID will be returned once the upload is completed.

4. Perform tasks

    ```py
    t = yd.submit_task(VideoSummaryTask(video_id=r.id))
    print(t())
    ```

For more examples, please visit the [Gradio Example(TODO: Add Link)]().

You can also use the command line interface to perform tasks demonstrated above:

```bash
$ yidong add_resource path/to/your/video.mp4

$ yidong submit_task VideoSummaryTask --video_id YOUR_VIDEO_ID
```
