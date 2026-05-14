#!/usr/bin/env python3
"""Upload video to YouTube using OAuth2 refresh token."""

import os
import json
import requests
from pathlib import Path

# OAuth credentials (set via environment variables or GitHub Secrets)
CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
    raise ValueError("Missing YouTube credentials. Set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN environment variables.")


def get_access_token():
    """Get a fresh access token using the refresh token."""
    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token"
        }
    )
    if response.status_code != 200:
        print(f"Token refresh failed: {response.status_code}")
        print(f"Response: {response.text}")
        response.raise_for_status()
    return response.json()["access_token"]


def upload_video(video_path: str, title: str, description: str, tags: list = None, privacy: str = "public"):
    """Upload a video to YouTube."""
    access_token = get_access_token()

    # Video metadata
    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or ["brainrot", "education", "facts", "shorts"],
            "categoryId": "27"  # Education category
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False
        }
    }

    # Resumable upload - Step 1: Initialize
    init_response = requests.post(
        "https://www.googleapis.com/upload/youtube/v3/videos",
        params={
            "uploadType": "resumable",
            "part": "snippet,status"
        },
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Upload-Content-Type": "video/mp4"
        },
        json=metadata
    )

    if init_response.status_code != 200:
        print(f"YouTube API Error: {init_response.status_code}")
        print(f"Response: {init_response.text}")
        init_response.raise_for_status()

    upload_url = init_response.headers["Location"]

    # Step 2: Upload the video
    video_size = Path(video_path).stat().st_size
    with open(video_path, "rb") as video_file:
        upload_response = requests.put(
            upload_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "video/mp4",
                "Content-Length": str(video_size)
            },
            data=video_file
        )

    upload_response.raise_for_status()
    result = upload_response.json()

    video_id = result["id"]
    print(f"Video uploaded successfully!")
    print(f"Video ID: {video_id}")
    print(f"URL: https://www.youtube.com/watch?v={video_id}")

    return video_id


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python youtube_upload.py <video_path> <title> [description]")
        sys.exit(1)

    video_path = sys.argv[1]
    title = sys.argv[2]
    description = sys.argv[3] if len(sys.argv) > 3 else "Educational brainrot content"

    upload_video(video_path, title, description)
