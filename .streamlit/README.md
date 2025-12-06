# Video Editor Pro 🎬

Professional video editing app with HDR effects for Streamlit Community Cloud.

## Features

✨ **Audio Sources**
- Upload audio files (MP3, WAV, M4A, AAC)
- Extract audio from YouTube videos

🎥 **Video Processing**
- Upload background videos (MP4, MOV, AVI, MKV)
- Use default video file
- Random timestamp cutting to match audio length
- High-quality output (1080x1920)

🎨 **HDR Effect**
- Customizable HDR settings
- Size, Amount, Strength controls
- Filters, Glow, Range adjustments
- Toggle on/off

⚙️ **Export Settings**
- 30fps or 60fps output
- High bitrate (8-10 Mbps)
- 1080x1920 vertical format
- Professional quality encoding

## Deployment on Streamlit Community Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy!

## Local Installation

```bash
pip install -r requirements.txt
```

### System Requirements

Install FFmpeg:
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

## Usage

1. Choose audio source (upload or YouTube URL)
2. Choose background video (upload or use default)
3. Adjust HDR settings if desired
4. Select frame rate (30fps or 60fps)
5. Click "Process Video"
6. Download your edited video!

## Default Video Path

For local use, update the default video path in `app.py`:
```python
default_path = r"D:\Satisfying 0307 (2).mp4"
```

Change this to your actual video file path.

## Links

- [StreamLadder App](https://streamladder.com)

## Tech Stack

- Streamlit
- FFmpeg
- yt-dlp
- Python 3.9+
