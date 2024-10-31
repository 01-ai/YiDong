import os
import logging
import requests
import gradio as gr
API_URL_TEMPLATE = "https://api-yidong.lingyiwanwu.com/v1/ops/api_key?user_email={user_email}&user_source=huggingface"

def get_user_info(profile: gr.OAuthProfile | None) -> str:
    def call_api(user_email):
        url = API_URL_TEMPLATE.format(user_email=user_email)
    
        headers = {
            'Authorization': '{}'.format(os.environ.get('auth'))
        }
        response = requests.post(url, headers=headers)
        logging.info("response:{}".format(response.json()["data"]["display_api_key"]))
        return response.json()["data"]["display_api_key"]
    

    if profile is None:
        return "User not logged in."
    logging.info(f"username: {profile.name}")
    return call_api(profile.name)

with gr.Blocks() as clip_service:   
    with gr.Row():
        login_button = gr.LoginButton()
        user_info_display = gr.Textbox(label="In order to get your user key, please click on huggingface login, the first time you login you will have the full key, please save it. After that your key will be hidden.",interactive=True) 
        m1 = gr.Markdown()
        clip_service.load(get_user_info,inputs=None,outputs=user_info_display)

        logging.info(f"The value of the current variable is: {user_info_display}")

clip_service.launch(share=True)