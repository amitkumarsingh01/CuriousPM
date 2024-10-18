import streamlit as st
import os
import io
import requests
import moviepy.editor as mp
from gtts import gTTS
import whisper
import tempfile

def main():
    st.set_page_config(layout="wide")
    st.title("Welcome to Curious PM")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Upload and Preview")
        video_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])

        if video_file is not None:
            # Save uploaded file to a temporary file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
                temp_video_file.write(video_file.read())
                temp_video_file_path = temp_video_file.name
            st.video(temp_video_file_path)

            # Add GitHub and Demo buttons below the video upload
            st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/amitkumarsingh01/CuriousPM)")
            st.markdown("[![Working Demo](https://img.shields.io/badge/Working-Demo-green)](https://www.canva.com/design/DAGT3jGhN58/sHbZFhJ5Cs7LWPcNYzFmug/view?utm_content=DAGT3jGhN58&utm_campaign=designshare&utm_medium=link&utm_source=editor)")

    if video_file is not None:
        with col2:
            st.header("Processing Outputs")
            audio_col1, audio_col2 = st.columns(2)

            # Process video and extract audio using moviepy
            video_clip = mp.VideoFileClip(temp_video_file_path)
            audio_clip = video_clip.audio
            audio_buffer = io.BytesIO()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio_file:
                audio_clip.write_audiofile(temp_audio_file.name, codec='mp3')
                temp_audio_file.seek(0)
                audio_buffer.write(temp_audio_file.read())

            audio_buffer.seek(0)

            # Display and download the original audio
            audio_col1.audio(audio_buffer, format='audio/mp3')
            audio_col1.download_button("Download Original Audio", audio_buffer, file_name="audio.mp3")

            # Transcription using Whisper
            model = whisper.load_model("base")
            audio_buffer.seek(0)
            result = model.transcribe(temp_audio_file.name)
            transcribed_text = result["text"]

            text_col1, text_col2 = st.columns(2)
            with st.container():
                text_col1.text_area("Original Transcribed Text", transcribed_text, height=200)
                transcribed_text_buffer = io.BytesIO(transcribed_text.encode())
                text_col1.download_button("Download Original Text", transcribed_text_buffer, file_name="transcription.txt")

                # Grammar correction using Azure OpenAI API
                azure_openai_key = "22ec84421ec24230a3638d1b51e3a7dc"
                azure_openai_endpoint = "https://internshala.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
                headers = {"Content-Type": "application/json", "api-key": azure_openai_key}
                prompt = f"Rewrite only corrected grammar: {transcribed_text}"
                data = {"messages": [{"role": "user", "content": prompt}], "max_tokens": 500}
                response = requests.post(azure_openai_endpoint, headers=headers, json=data)

                if response.status_code == 200:
                    corrected_text = response.json()["choices"][0]["message"]["content"].strip()
                    text_col2.text_area("Corrected Text", corrected_text, height=200)
                    corrected_text_buffer = io.BytesIO(corrected_text.encode())
                    text_col2.download_button("Download Corrected Text", corrected_text_buffer, file_name="corrected_text.txt")

                    # Generate corrected audio using gTTS
                    corrected_audio_buffer = io.BytesIO()
                    tts = gTTS(corrected_text)
                    tts.write_to_fp(corrected_audio_buffer)
                    corrected_audio_buffer.seek(0)

                    # Sync corrected audio to match original duration
                    original_duration = mp.AudioFileClip(temp_audio_file.name).duration
                    corrected_audio_clip = mp.AudioFileClip(corrected_audio_buffer)
                    adjusted_audio_clip = corrected_audio_clip.fx(mp.vfx.speedx, corrected_audio_clip.duration / original_duration)
                    
                    adjusted_audio_buffer = io.BytesIO()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as adjusted_audio_temp_file:
                        adjusted_audio_clip.write_audiofile(adjusted_audio_temp_file.name)
                        adjusted_audio_temp_file.seek(0)
                        adjusted_audio_buffer.write(adjusted_audio_temp_file.read())
                    adjusted_audio_buffer.seek(0)

                    audio_col2.audio(adjusted_audio_buffer, format='audio/mp3')
                    audio_col2.download_button("Download Adjusted Audio", adjusted_audio_buffer, file_name="adjusted_audio.mp3")

                    # Final video processing with the corrected audio
                    video_col1, video_col2 = st.columns(2)
                    video_no_audio_clip = video_clip.without_audio()

                    # Save video without audio to temporary file
                    video_no_audio_buffer = io.BytesIO()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_no_audio_file:
                        video_no_audio_clip.write_videofile(temp_no_audio_file.name, codec='libx264')
                        temp_no_audio_file.seek(0)
                        video_no_audio_buffer.write(temp_no_audio_file.read())
                    video_no_audio_buffer.seek(0)

                    video_col1.video(video_no_audio_buffer)
                    video_col1.download_button("Download Video without Audio", video_no_audio_buffer, file_name="video_no_audio.mp4")

                    # Merge corrected audio with the video
                    final_video_clip = video_no_audio_clip.set_audio(corrected_audio_clip)
                    final_video_buffer = io.BytesIO()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_final_video_file:
                        final_video_clip.write_videofile(temp_final_video_file.name, codec='libx264')
                        temp_final_video_file.seek(0)
                        final_video_buffer.write(temp_final_video_file.read())
                    final_video_buffer.seek(0)

                    video_col2.video(final_video_buffer)
                    video_col2.download_button("Download Final Video", final_video_buffer, file_name="final_video.mp4")

                else:
                    st.error(f"Failed to connect to Azure OpenAI: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()
