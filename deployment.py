import streamlit as st
import os
import requests
import moviepy.editor as mp
from gtts import gTTS
import whisper

def ensure_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def main():
    st.set_page_config(layout="wide")
    st.title("Welcome to Curious PM")

    # Directories for storing input and output files in /tmp for Streamlit Cloud
    input_dir = "/tmp/input"
    output_dir = "/tmp/output"
    
    ensure_directory(input_dir)
    ensure_directory(output_dir)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("Upload and Preview")
        video_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi"])
        serial_number = len(os.listdir(input_dir)) + 1

        if video_file is not None:
            input_video_path = os.path.join(input_dir, f"input{serial_number}.mp4")
            with open(input_video_path, "wb") as f:
                f.write(video_file.read())
            st.video(input_video_path)

            # Add GitHub and Demo buttons below the video upload
            st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/amitkumarsingh01/CuriousPM)")
            st.markdown("[![Working Demo](https://img.shields.io/badge/Working-Demo-green)](https://www.canva.com/design/DAGT3jGhN58/sHbZFhJ5Cs7LWPcNYzFmug/view?utm_content=DAGT3jGhN58&utm_campaign=designshare&utm_medium=link&utm_source=editor)")

    if video_file is not None:
        with col2:
            st.header("Processing Outputs")
            audio_col1, audio_col2 = st.columns(2)
            audio_clip = mp.VideoFileClip(input_video_path).audio
            audio_path = os.path.join(output_dir, f"audio{serial_number}.mp3")
            audio_clip.write_audiofile(audio_path)
            audio_col1.audio(audio_path, format='audio/mp3')
            with open(audio_path, 'rb') as f:
                audio_col1.download_button("Download Original Audio", f, file_name=f"audio{serial_number}.mp3")

            # Transcription and processing
            model = whisper.load_model("base")
            result = model.transcribe(audio_path)
            transcribed_text = result["text"]

            text_col1, text_col2 = st.columns(2)
            with st.container():
                text_col1.text_area("Original Transcribed Text", transcribed_text, height=200)
                transcribed_text_path = os.path.join(output_dir, f"transcription{serial_number}.txt")
                with open(transcribed_text_path, "w") as f:
                    f.write(transcribed_text)
                with open(transcribed_text_path, 'rb') as f:
                    text_col1.download_button("Download Original Text", f, file_name=f"transcription{serial_number}.txt")

                # Grammar correction using Azure OpenAI API
                azure_openai_key = "AZURE_OPENAI_API"
                azure_openai_endpoint = "https://internshala.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
                headers = {"Content-Type": "application/json", "api-key": azure_openai_key}
                prompt = f"Rewrite only corrected grammar: {transcribed_text}"
                data = {"messages": [{"role": "user", "content": prompt}], "max_tokens": 500}
                response = requests.post(azure_openai_endpoint, headers=headers, json=data)

                if response.status_code == 200:
                    corrected_text = response.json()["choices"][0]["message"]["content"].strip()
                    text_col2.text_area("Corrected Text", corrected_text, height=200)
                    corrected_text_path = os.path.join(output_dir, f"corrected_text{serial_number}.txt")
                    with open(corrected_text_path, "w") as f:
                        f.write(corrected_text)
                    with open(corrected_text_path, 'rb') as f:
                        text_col2.download_button("Download Corrected Text", f, file_name=f"corrected_text{serial_number}.txt")

                    # Generate corrected audio using gTTS
                    corrected_audio_path = os.path.join(output_dir, f"corrected_audio{serial_number}.mp3")
                    tts = gTTS(corrected_text)
                    tts.save(corrected_audio_path)

                    original_duration = mp.AudioFileClip(audio_path).duration
                    corrected_audio_clip = mp.AudioFileClip(corrected_audio_path)
                    adjusted_audio = corrected_audio_clip.fx(mp.vfx.speedx, corrected_audio_clip.duration / original_duration)
                    adjusted_audio_path = os.path.join(output_dir, f"adjusted_audio{serial_number}.mp3")
                    adjusted_audio.write_audiofile(adjusted_audio_path)

                    audio_col2.audio(adjusted_audio_path, format='audio/mp3')
                    with open(adjusted_audio_path, 'rb') as f:
                        audio_col2.download_button("Download Adjusted Audio", f, file_name=f"adjusted_audio{serial_number}.mp3")

                    # Final video processing
                    video_col1, video_col2 = st.columns(2)
                    video_no_audio_path = os.path.join(output_dir, f"video_no_audio{serial_number}.mp4")
                    video_no_audio = mp.VideoFileClip(input_video_path).without_audio()
                    video_no_audio.write_videofile(video_no_audio_path)
                    video_col1.video(video_no_audio_path)
                    with open(video_no_audio_path, 'rb') as f:
                        video_col1.download_button("Download Video without Audio", f, file_name=f"video_no_audio{serial_number}.mp4")

                    final_video_path = os.path.join(output_dir, f"final_video{serial_number}.mp4")
                    final_audio_clip = mp.AudioFileClip(adjusted_audio_path)
                    final_video = video_no_audio.set_audio(final_audio_clip)
                    final_video.write_videofile(final_video_path)
                    video_col2.video(final_video_path)
                    with open(final_video_path, 'rb') as f:
                        video_col2.download_button("Download Final Video", f, file_name=f"final_video{serial_number}.mp4")

                else:
                    st.error(f"Failed to connect to Azure OpenAI: {response.status_code} - {response.text}")

if __name__ == "__main__":
    main()
