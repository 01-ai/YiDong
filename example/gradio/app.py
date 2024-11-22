import logging
import os

import gradio as gr
import requests
from huggingface_hub import whoami

API_URL_TEMPLATE = "https://api-yidong.lingyiwanwu.com/v1/ops/api_key?user_email={user_email}&user_source=huggingface"


def get_user_email(oauth_token: gr.OAuthToken | None) -> str | None:
    def call_api(user_email):
        url = API_URL_TEMPLATE.format(user_email=user_email)
        headers = {"Authorization": os.getenv("AUTH")}
        response = requests.post(url, headers=headers)
        return response.json()["data"]["display_api_key"]

    if oauth_token is None:
        return None
    user_info = whoami(token=oauth_token.token)
    email = user_info.get("email")
    return call_api(email)


with gr.Blocks() as clip_service:
    with gr.Row():
        login_button = gr.LoginButton()
        user_email_display = gr.Textbox(
            label="In order to get your user key, please click on huggingface login, the first time you login you will have the full key, please save it. After that your key will be hidden.",
            interactive=True,
        )
        clip_service.load(get_user_email, inputs=None, outputs=user_email_display)
        logging.info(f"The value of the current variable is: {user_email_display}")


if __name__ == "__main__":
    clip_service.queue(
        max_size=10,
        default_concurrency_limit=10,
    )

    clip_service.launch(ssr_mode=False)