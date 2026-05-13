#!/usr/bin/env python3
"""Main script: Pick topic, generate brainrot video, upload to YouTube."""

import os
import json
import subprocess
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
TOPICS_FILE = SCRIPT_DIR / "topics.json"
KOKORO_SCRIPT = SCRIPT_DIR / "kokoro_script.txt"
OUTPUT_VIDEO = SCRIPT_DIR / "final_video_with_subs.mp4"


def load_topics():
    """Load topics from JSON file."""
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_topics(data):
    """Save topics back to JSON file."""
    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_next_topic(data):
    """Get the next topic in rotation."""
    topics = data["topics"]
    index = data["current_index"]
    topic = topics[index]

    # Update index for next run (circular)
    data["current_index"] = (index + 1) % len(topics)
    save_topics(data)

    return topic


def write_script(script_text):
    """Write the script to kokoro_script.txt."""
    with open(KOKORO_SCRIPT, "w", encoding="utf-8") as f:
        f.write(script_text)
    print(f"Script written to {KOKORO_SCRIPT}")


def generate_video():
    """Run pdf2brainrot.py to generate video."""
    print("Generating brainrot video...")
    result = subprocess.run(
        ["python", "pdf2brainrot.py"],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error generating video: {result.stderr}")
        raise Exception("Video generation failed")
    print("Video generated successfully!")


def upload_to_youtube(title, description):
    """Upload video to YouTube."""
    print(f"Uploading to YouTube: {title}")
    from youtube_upload import upload_video

    video_id = upload_video(
        video_path=str(OUTPUT_VIDEO),
        title=title,
        description=description,
        tags=["brainrot", "education", "facts", "shorts", "hindi", "science"],
        privacy="public"
    )
    return video_id


def main():
    """Main workflow."""
    print("=" * 50)
    print("BRAINROT GENERATOR + YOUTUBE UPLOADER")
    print("=" * 50)

    # Load topics
    data = load_topics()
    topic = get_next_topic(data)

    print(f"\nTopic: {topic['id']}")
    print(f"Title: {topic['title']}")

    # Write script
    write_script(topic["script"])

    # Generate video
    generate_video()

    # Upload to YouTube
    description = f"""Educational brainrot content - {topic['title']}

Facts presented in an engaging, fast-paced format.
Subscribe for daily mind-blowing facts!

#shorts #education #facts #science #brainrot
"""

    video_id = upload_to_youtube(topic["title"], description)
    print(f"\nVideo live at: https://www.youtube.com/watch?v={video_id}")
    print("=" * 50)


if __name__ == "__main__":
    main()
