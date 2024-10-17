# Video and Audio Processing with Azure OpenAI

This project provides a web-based interface for processing video files. Users can upload a video, extract its audio, transcribe it using OpenAI's Whisper, correct the transcription with Azure OpenAI, and download the processed audio, text, and video.

### Features

- Upload and preview video files.
- Extract audio from the uploaded video.
- Transcribe audio using OpenAI Whisper.
- Correct transcription using Azure OpenAI (GPT-4).
- Convert corrected text to speech using Google Text-to-Speech (gTTS).
- Download the processed audio, transcription, and final video.

### Installation

#### Make sure to do the following changes
```
azure_openai_key = "AZURE_OPENAI_API"
```

```
git clone https://github.com/amitkumarsingh01/CuriousPM.git
```
```
cd CuriousPM
pip install -r requirements.txt
```
```
streamlit run solution.py
```
### Libraries

- Streamlit: Provides the web interface for the application.
- MoviePy: Handles video and audio processing.
- gTTS (Google Text-to-Speech): Converts corrected text to speech.
- Requests: Used to make API calls to Azure OpenAI.
- Whisper: Performs audio transcription (installed via GitHub).
- NumPy: Required by MoviePy and Whisper for numerical operations.

