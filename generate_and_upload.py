#!/usr/bin/env python3
"""Main script: Pick topic, generate brainrot video, upload to YouTube with SEO optimization."""

import os
import json
import subprocess
import random
from pathlib import Path
from datetime import datetime

# Paths
SCRIPT_DIR = Path(__file__).parent
TOPICS_FILE = SCRIPT_DIR / "topics.json"
KOKORO_SCRIPT = SCRIPT_DIR / "kokoro_script.txt"
OUTPUT_VIDEO = SCRIPT_DIR / "final_video_with_subs.mp4"

# SEO Configuration
TITLE_HOOKS = [
    "🤯", "😱", "🔥", "💀", "⚡", "🧠", "😵", "🚀", "💯", "🎯"
]

# Subject-specific tags based on topic keywords
SUBJECT_TAGS = {
    "physics": ["physics", "physicsfacts", "science", "iitjee", "jee"],
    "chemistry": ["chemistry", "chemistryfacts", "organicchemistry", "jee"],
    "biology": ["biology", "biologyfacts", "neet", "mbbs", "science"],
    "math": ["mathematics", "mathfacts", "calculus", "jee"],
    "space": ["space", "astronomy", "universe", "cosmos", "nasa"],
    "brain": ["brain", "neuroscience", "psychology", "mindblown"],
    "dna": ["genetics", "dna", "biology", "neet", "science"],
    "evolution": ["evolution", "biology", "darwin", "neet"],
    "quantum": ["quantumphysics", "physics", "science", "iitjee"],
    "ocean": ["ocean", "marinelife", "nature", "science"],
    "default": ["science", "facts", "education", "knowledge"]
}

# Core hashtags that always perform well
CORE_HASHTAGS = ["shorts", "viral", "facts", "mindblown"]
HINDI_HASHTAGS = ["hindifacts", "hindiknowledge"]
INDIA_HASHTAGS = ["india", "trending"]


def detect_subject(topic_id: str, title: str) -> list:
    """Detect subject from topic ID and return relevant tags."""
    topic_lower = topic_id.lower() + " " + title.lower()

    for subject, tags in SUBJECT_TAGS.items():
        if subject in topic_lower:
            return tags

    # Check for common keywords
    if any(kw in topic_lower for kw in ["cell", "mitochondria", "photosynthesis"]):
        return SUBJECT_TAGS["biology"]
    if any(kw in topic_lower for kw in ["black hole", "star", "galaxy", "universe"]):
        return SUBJECT_TAGS["space"]
    if any(kw in topic_lower for kw in ["newton", "gravity", "force", "motion"]):
        return SUBJECT_TAGS["physics"]

    return SUBJECT_TAGS["default"]


def generate_optimized_title(original_title: str) -> str:
    """Generate SEO-optimized title under 70 chars with hook emoji."""
    hook = random.choice(TITLE_HOOKS)

    # Clean up title if too long
    title = original_title.strip()
    if len(title) > 60:
        title = title[:57] + "..."

    # Add hook at start
    optimized = f"{hook} {title}"

    return optimized[:70]  # Hard cap at 70 chars


def generate_optimized_tags(topic_id: str, title: str) -> list:
    """Generate optimized tag list (mix of niche + trending)."""
    subject_tags = detect_subject(topic_id, title)

    # Build tag list: subject-specific + core + hindi + india
    tags = []
    tags.extend(subject_tags[:3])  # Top 3 subject tags
    tags.extend(CORE_HASHTAGS[:2])  # 2 core tags
    tags.extend(HINDI_HASHTAGS[:1])  # 1 Hindi tag
    tags.append("brainrot")
    tags.append("chinu")  # Character branding

    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)

    return unique_tags[:10]  # Max 10 tags


def generate_optimized_description(title: str, topic_id: str) -> str:
    """Generate SEO-optimized description with hashtags."""
    subject_tags = detect_subject(topic_id, title)

    # Build hashtag string (3-5 hashtags in description)
    hashtags = ["#shorts", "#facts"]
    hashtags.extend([f"#{tag}" for tag in subject_tags[:2]])
    hashtags.append("#brainrot")

    hashtag_str = " ".join(hashtags[:5])

    description = f"""{title}

Chinu explains complex topics in desi style 🔥
Subscribe for daily mind-blowing facts!

{hashtag_str}

📚 Follow for more:
• Science facts that'll make you go 🤯
• JEE/NEET concepts made fun
• Daily knowledge bombs

#education #hindi #india #viral #trending
"""
    return description


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


def upload_to_youtube(title, description, tags):
    """Upload video to YouTube with optimized metadata."""
    print(f"Uploading to YouTube: {title}")
    from youtube_upload import upload_video

    video_id = upload_video(
        video_path=str(OUTPUT_VIDEO),
        title=title,
        description=description,
        tags=tags,
        privacy="public"
    )
    return video_id


def generate_thumbnail_for_topic(title: str, topic_id: str) -> str:
    """Generate thumbnail for the topic."""
    from thumbnail_generator import generate_thumbnail

    thumbnail_path = str(SCRIPT_DIR / "thumbnail.png")
    generate_thumbnail(title, topic_id, thumbnail_path)
    return thumbnail_path


def main():
    """Main workflow with SEO optimization."""
    print("=" * 50)
    print("BRAINROT GENERATOR + YOUTUBE UPLOADER (SEO OPTIMIZED)")
    print("=" * 50)

    # Load topics
    data = load_topics()
    topic = get_next_topic(data)

    print(f"\nTopic: {topic['id']}")
    print(f"Original Title: {topic['title']}")

    # Generate SEO-optimized metadata
    optimized_title = generate_optimized_title(topic["title"])
    optimized_tags = generate_optimized_tags(topic["id"], topic["title"])
    optimized_description = generate_optimized_description(topic["title"], topic["id"])

    print(f"Optimized Title: {optimized_title}")
    print(f"Tags: {optimized_tags}")

    # Write script
    write_script(topic["script"])

    # Generate video
    generate_video()

    # Generate thumbnail
    print("Generating thumbnail...")
    thumbnail_path = generate_thumbnail_for_topic(topic["title"], topic["id"])
    print(f"Thumbnail generated: {thumbnail_path}")

    # Upload to YouTube with optimized metadata
    video_id = upload_to_youtube(optimized_title, optimized_description, optimized_tags)

    # Upload custom thumbnail
    print("Uploading thumbnail...")
    from youtube_upload import upload_thumbnail
    upload_thumbnail(video_id, thumbnail_path)

    print(f"\n✅ Video live at: https://www.youtube.com/watch?v={video_id}")
    print(f"🖼️ Custom thumbnail uploaded")
    print(f"📊 Tags used: {', '.join(optimized_tags)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
