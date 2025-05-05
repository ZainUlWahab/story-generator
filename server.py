import grpc
from concurrent import futures
from typing import List
from trendspy import Trends
import os
import torch
from TTS.api import TTS
from transformers import AutoModelForCausalLM, AutoTokenizer
import re
import io
import sys
from pyngrok import ngrok, conf

NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
conf.get_default().auth_token = NGROK_AUTH_TOKEN
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

os.environ["COQUI_TOS_AGREED"] = "1"

# Uncomment the below line if working on a local machine please
sys.path.append("/kaggle/input/project-learning")
import nlp_project_pb2
import nlp_project_pb2_grpc

tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
speaker_wav = "/kaggle/input/sahal-voice/sahal_voice.wav" # Change your speaker wav accordinly please hehe

USE_API = False
if USE_API:
    from google import genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    client = genai.GenerativeModel("gemini-pro")


class NLP_ProjectServicer(nlp_project_pb2_grpc.nlp_projectServicer):
    def __init__(self):
        self.model_name = "Qwen/Qwen2.5-7B-Instruct"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name, torch_dtype="auto", device_map="auto")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def get_trends(self, request, context):
        try:
            if not request.country_code or not request.theme:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Country code and theme must be provided.")
                return nlp_project_pb2.trends(
                    result="",
                    story="",
                    audio=b"",
                    status="error",
                    message="Country code and theme must be provided."
                )

            trends_list = self.fetch_google_trends(request.country_code)
            if not trends_list:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("No trends found. Invalid country code or API error.")
                return nlp_project_pb2.trends(
                    result="",
                    story="",
                    audio=b"",
                    status="error",
                    message="No trends found. Invalid country code or API error."
                )


            trends = ", ".join(trends_list)
            story = self.generate_story(request.theme, trends)

            audio_bytes = b""
            if request.generate_audio:
                audio_bytes = self.generate_audio(story)

            return nlp_project_pb2.trends(
                result=trends,
                story=story,
                audio=audio_bytes,
                status="success",
                message="Trends and story generated successfully"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Server error: {e}")
            return nlp_project_pb2.trends(
                result="",
                story="",
                audio=b"",
                status="error",
                message=str(e)
            )

    def fetch_google_trends(self, country: str) -> List[str]:
        try:
            tr = Trends()
            trends = tr.trending_now(geo=country)
            return [trend.keyword for trend in trends[:5]]
        except Exception as e:
            print(f"[Error] Failed to fetch Google trends: {e}")
            return []

    def generate_story(self, theme: str, trends: str) -> str:
        prompt = (
            f"Write a short story (100-150 words) in the {theme} genre. "
            f"Incorporate the following trending topics: {trends}. "
            f"Ensure the story feels cohesive and engaging."
        )
        try:
            if USE_API:
                response = client.generate_content(prompt)
                return response.text.strip() if response.text else "No story generated."
            else:
                messages = [
                    {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
                text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
                output_ids = self.model.generate(**model_inputs, max_new_tokens=400)
                output_ids = [out[len(inp):] for inp, out in zip(model_inputs.input_ids, output_ids)]
                story = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)[0]
                return story
        except Exception as e:
            return f"Error during story generation: {e}"

    def generate_audio(self, text: str) -> bytes:
        try:
            with io.BytesIO() as buf:
                tts_model.tts_to_file(
                    text=text,
                    file_path="temp.wav",
                    speaker_wav=speaker_wav,
                    language="en"
                )
                with open("temp.wav", "rb") as f:
                    audio_data = f.read()
                os.remove("temp.wav")
                return audio_data
        except Exception as e:
            print(f"Audio generation error: {e}")
            return b""


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    nlp_project_pb2_grpc.add_nlp_projectServicer_to_server(NLP_ProjectServicer(), server)
    port = 50051
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    public_url = ngrok.connect(port, "tcp")
    print(f"Server started on localhost:{port}")
    print(f"Public gRPC URL (ngrok): {public_url}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()