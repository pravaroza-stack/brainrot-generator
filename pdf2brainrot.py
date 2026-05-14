import os
import argparse
import asyncio
from typing import List, Dict
import torch
import numpy as np
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, concatenate_videoclips
import whisper_timestamped as whisper

# Paths
BASE_VIDEO = "videoplayback.mp4"
SCRIPT_PATH = "kokoro_script.txt"
OUTPUT_VIDEO = "final_video.mp4"
FONT_PATH = "./Roboto-ExtraBold.ttf"
TTS_AUDIO_PATH = "tts_output.mp3"

# GPU acceleration if available
device = "cuda" if torch.cuda.is_available() else "cpu"


async def generate_tts_audio_hindi(text: str, output_path: str = "tts_output.mp3") -> str:
    """Generate TTS audio using edge-tts with Hindi voice."""
    import edge_tts

    # Hindi male voice - sounds natural for brainrot content
    voice = "hi-IN-MadhurNeural"  # Hindi male voice

    communicate = edge_tts.Communicate(text, voice, rate="+10%")
    await communicate.save(output_path)

    print(f"✅ Hindi TTS audio saved as {output_path}")
    return output_path


def generate_tts_audio(text: str) -> str:
    """Wrapper to run async TTS generation."""
    return asyncio.run(generate_tts_audio_hindi(text))


def extract_timestamps(audio_path: str) -> List[Dict[str, str | float]]:
    """Extract timestamps using Whisper with Hindi language detection."""
    audio = whisper.load_audio(audio_path)

    model = whisper.load_model("small", device=device)

    # Use Hindi language for better transcription
    result = whisper.transcribe(model, audio, language="hi")

    word_timestamps = []
    for items in result["segments"]:
        for item in items["words"]:
            word_timestamps.append({
                "text": item["text"],
                "start": item["start"],
                "duration": round(float(item["end"]) - float(item["start"]), 5)
            })

    print(f"✅ Extracted {len(word_timestamps)} timestamps")
    return word_timestamps


def overlay_audio_on_video(video_path: str, audio_path: str, output_path: str) -> None:
    """Overlay TTS audio onto video, looping video if needed."""
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    # Loop video if audio is longer than video
    if audio.duration > video.duration:
        loops_needed = int(audio.duration // video.duration) + 1
        video = concatenate_videoclips([video] * loops_needed)
        print(f"🔁 Looped video {loops_needed}x to match audio duration")

    video = video.subclipped(0, audio.duration).with_audio(audio)
    video.write_videofile(output_path, codec="libx264", fps=video.fps)

    print(f"✅ Final video saved as {output_path}")


def overlay_text_on_video(video_path: str, aligned_words, output_path: str) -> None:
    """Overlay synchronized subtitles."""
    video = VideoFileClip(video_path)
    text_clips = []

    for i, word_data in enumerate(aligned_words):
        word, start_time, duration = word_data["text"], word_data["start"], word_data["duration"]
        start_time = max(0, start_time)

        txt_clip = (TextClip(
                        text=word,
                        font_size=70,
                        font=FONT_PATH,
                        color='white',
                        stroke_color='black',
                        stroke_width=7,
                        size=(720, 100)
                    )
                    .with_position("center")
                    .with_duration(duration)
                    .with_start(start_time))

        text_clips.append(txt_clip)

    final_video = CompositeVideoClip([video] + text_clips)
    final_video.write_videofile(output_path, codec="libx264", fps=video.fps)

    print(f"✅ Final video with subtitles saved as {output_path}")


def main() -> None:
    """Main function to generate brainrot with subtitles."""
    # Read script text
    with open(SCRIPT_PATH, "r", encoding="utf-8") as file:
        script_text = file.read().strip()

    # Generate TTS audio (Hindi)
    print("🔊 Generating Hindi TTS audio...")
    tts_audio_file = generate_tts_audio(script_text)

    # Overlay audio onto video
    print("🎞️ Overlaying audio onto video...")
    overlay_audio_on_video(BASE_VIDEO, tts_audio_file, OUTPUT_VIDEO)

    # Extract raw timestamps
    print("🕒 Extracting timestamps...")
    word_timestamps = extract_timestamps(tts_audio_file)

    # Overlay synchronized subtitles
    print("📝 Overlaying synchronized subtitles...")
    overlay_text_on_video(OUTPUT_VIDEO, word_timestamps, "final_video_with_subs.mp4")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate brainrot video with Hindi TTS.")
    args = parser.parse_args()
    main()
