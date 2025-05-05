# NLP Trends & Story Generator

A full-stack application that fetches trending topics from Google Trends based on country code, generates creative stories incorporating those trends, and optionally creates audio narration using text-to-speech technology.

## 📋 Features

- **Real-time Google Trends**: Fetch the latest trending topics by country code
- **AI-powered Story Generation**: Create unique stories using Qwen 2.5 7B LLM
- **Text-to-Speech**: Convert generated stories to natural-sounding audio
- **Theme Selection**: Customize the genre of your generated stories (Fantasy, Sci-Fi, Mystery, etc.)
- **Web Interface**: Simple Gradio UI for interacting with the system
- **Microservice Architecture**: Client-server model using gRPC for efficient communication

## 🏗️ Architecture

The application follows a client-server architecture using gRPC for communication:

```
┌─────────────┐     gRPC      ┌─────────────┐
│             │◄────────────► │             │
│  Client UI  │     Proto     │   Server    │
│  (Gradio)   │               │  Services   │
└─────────────┘               └─────────────┘
                                     │
                              ┌──────┴───────┐
                              │              │
                      ┌───────┴────┐  ┌──────┴─────┐
                      │            │  │            │
                ┌─────┴─────┐ ┌────┴──┴──┐  ┌──────┴─────┐
                │           │ │          │  │            │
                │  Google   │ │  Qwen2.5 │  │   XTTS     │
                │  Trends   │ │    LLM   │  │    TTS     │
                │           │ │          │  │            │
                └───────────┘ └──────────┘  └────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- NGROK Authentication Token (for exposing the gRPC server)
- (Optional) Gemini API Key (if using Google's Gemini Pro instead of local LLM)

### Environment Setup

1. Create a `.env` file in the project root with the following:

```
NGROK_AUTH_TOKEN=your_ngrok_auth_token
GEMINI_API_KEY=your_gemini_api_key  # Optional, only if USE_API=True
```

2. Prepare a voice sample file for text-to-speech (default path in server.py: `/kaggle/input/sahal-voice/sahal_voice.wav`)

### Running with Docker

The project includes Docker and Docker Compose configurations for easy deployment:

```bash
# Build and start the containers
docker-compose up -d

# Check the logs for the NGROK public URL
docker-compose logs server
```

## 📊 Usage

1. **Start the application**: Access the Gradio web interface (URL provided in logs)
2. **Enter parameters**:
   - Country Code (e.g., "US", "PK", "IN")
   - Theme/Genre (e.g., "Fantasy", "Sci-Fi", "Mystery")
   - Toggle "Generate Audio" if you want audio narration
3. **Submit**: Click the submit button to generate your story
4. **Results**: View the trending topics, story, and play audio (if generated)

## 💻 API Reference

### Proto Definition

```protobuf
service nlp_project {
  rpc get_trends(get_trends_request) returns (trends);
}

message get_trends_request {
  string country_code = 1;
  string theme = 2;
  bool generate_audio = 3;
}

message trends {
  string result = 1;
  string story = 2;
  bytes audio = 3;
  string status = 4;
  string message = 5;
}
```

### API Testing
- The api was tested thoroughly using the Postman collection. The link to the collection is here [link](https://www.postman.com/zainulwahab/workspace/zain-ul-wahab-s-workspace/collection/6817aef0cccde77c367fe9a8?action=share&creator=44661341)

## 🧠 Models & Technologies

### Core Technologies
- **gRPC**: High-performance RPC framework for service communication
- **Gradio**: Web UI framework for machine learning applications
- **Docker**: Containerization for consistent deployment
- **NGROK**: Secure tunneling for exposing local servers

### AI Models
- **Text Generation**: [Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) (Alibaba Cloud)
- **Text-to-Speech**: [XTTS v2](https://huggingface.co/coqui/XTTS-v2) (Multilingual TTS model)
- **Alternative**: Google's Gemini Pro (when `USE_API` is set to `True`)

### Libraries
- **TrendsPy**: Python API for Google Trends data
- **PyTorch**: Deep learning framework
- **Transformers**: Hugging Face library for state-of-the-art NLP
- **TTS**: Coqui TTS library for text-to-speech synthesis

## ⚠️ Limitations

- **Resource Requirements**: Running the LLM and TTS models locally requires significant computational resources (GPU recommended)
- **NGROK Limitations**: Free tier has connection and bandwidth constraints
- **Google Trends API**: May have rate limits for frequent requests
- **Story Quality**: Generated stories are limited by the capabilities of the underlying model
- **Audio Generation**: TTS requires a good quality speaker reference sample for optimal results

## 🎬 Demo
https://github.com/ZainUlWahab/story-generator/blob/main/nlp_project_demo.mp4
The demo video showcases the application's functionality from entering a country code and theme to receiving generated content and audio output.
## 📝 Development Notes

- Set `USE_API=True` in `server.py` to use Google's Gemini Pro instead of the local Qwen model
- Modify the speaker reference file path in `server.py` to use your custom voice
- The server is configured to run on Kaggle by default (note the path adjustment for Kaggle in `server.py`)

## 👏 Acknowledgements

- [TrendsPy](https://github.com/jayfk/trendspy) for Google Trends integration
- [Coqui TTS](https://github.com/coqui-ai/TTS) for the XTTS speech synthesis model
- [Qwen Team](https://huggingface.co/Qwen) for the language model
- [Gradio](https://gradio.app/) for the web interface framework
