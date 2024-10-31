from http import server
import os
import logging
import requests
import gradio as gr
from starlette.responses import RedirectResponse


def hello(profile: gr.OAuthProfile | None) -> str:
    # ^ expect a gr.OAuthProfile object as input to get the user's profile
    # if the user is not logged in, profile will be None
    if profile is None:
        return "I don't know you."
    return f"Hello {profile.name}"


# 定义函数执行 POST 请求


def get_user_info(profile: gr.OAuthProfile | None) -> str:
    def call_api(user_email):
        url = f"https://api-yidong.lingyiwanwu.com/v1/ops/api_key?user_email={user_email}&user_source=huggingface"
    
        headers = {
            'Authorization': '{}'.format(os.environ.get('auth'))
        }
        
        # 发送 POST 请求
        response = requests.post(url, headers=headers)
        logging.info("打印具体的响应值: {}".format(response.json()["data"]["display_api_key"]))
        
        
        # 返回响应内容
        '''{"code":0,"message":"Success","data":{"user_id":"07787cc6-9291-11ef-9ec5-ae87c86d3382","api_key_id":"07d53ee8-9291-11ef-9ec5-ae87c86d3382","display_api_key":"tOYnyKqwosGEhtIKNWQgVAol1dhqJ3HN","api_key_name":"","created_at":"2024-10-25T05:21:47.111000Z"}'''
        return response.json()["data"]["display_api_key"]
    

    if profile is None:
        return "User not logged in."
    

    logging.info(f"用户名: {profile.name}")
    return call_api(profile.name)

with gr.Blocks() as clip_service:
    
    with gr.Row():
        

        login_button = gr.LoginButton()
        user_info_display = gr.Textbox(label="为获取用户密钥，请点击huggingface登陆，第一次登陆时会有完整密钥，请保存。之后会隐藏您的密钥。",interactive=True)  # 用于显示用户信息
        m1 = gr.Markdown()
        clip_service.load(get_user_info,inputs=None,outputs=user_info_display)
        # 当用户点击登录按钮并完成 OAuth 登录后，调用 display_user_info 函数
        # login_button.click(get_user_info, inputs=None, outputs=[user_info_display])
        logging.info(f"当前变量的值是: {user_info_display}")

clip_service.launch(share=True)