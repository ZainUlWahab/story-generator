import gradio as gr
import grpc
from dotenv import load_dotenv
import os
import sys
import torch
import re
import nlp_project_pb2
import nlp_project_pb2_grpc

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
load_dotenv()

# Function to call the gRPC server
def get_trends(country_code, theme, generate_audio):
    try:
        if not country_code or not theme:
            return "Please enter a valid country code and theme.", None

        server_address = "8.tcp.ngrok.io:11078"  # Change to ngrok if needed
        with grpc.insecure_channel(server_address) as channel:
            stub = nlp_project_pb2_grpc.nlp_projectStub(channel)
            request = nlp_project_pb2.get_trends_request(
                country_code=country_code,
                theme=theme,
                generate_audio=generate_audio
            )
            response = stub.get_trends(request)

            trends = response.result
            story = response.story

            result_text = f"📈 Trends in {country_code}:\n{trends}\n\n📖 Story:\n{story}"

            audio_path = None
            if response.audio:
                audio_path = "output_from_server.wav"
                with open(audio_path, "wb") as f:
                    f.write(response.audio)

            return result_text, audio_path
    except grpc.RpcError as e:
        return f"Error communicating with server: {e.details()}", None
    except Exception as e:
        return f"An unexpected error occurred: {e}", None

demo = gr.Interface(
    fn=get_trends,
    inputs=[
        gr.Textbox(label="Country Code", placeholder='e.g., "PK" or "US"'),
        gr.Textbox(label="Theme", placeholder='e.g., Fantasy, Sci-fi, Mystery'),
        gr.Checkbox(label="Generate Audio")
    ],
    outputs=[
        gr.Textbox(label="AI-Generated Story & Trends"),
        gr.Audio(label="Generated Audio", type="filepath")
    ],
    title="NLP Project: Trends + Story Generator",
    description="Enter your country code and a theme. The app fetches trending topics, generates a short story using AI, and optionally creates audio narration."
)

demo.launch(share=True)