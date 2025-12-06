import streamlit as st
import os
import tempfile
import subprocess
import random
from pathlib import Path
import shutil

# Page config
st.set_page_config(page_title="Video Editor Pro", page_icon="🎬", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
    }
    .effect-panel {
        background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #667eea44;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🎬 Video Editor Pro</h1>', unsafe_allow_html=True)

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False

def get_audio_duration(audio_path):
    """Get duration of audio file in seconds"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return float(result.stdout.strip())
    except:
        return None

def get_video_duration(video_path):
    """Get duration of video file in seconds"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return float(result.stdout.strip())
    except:
        return None

def extract_youtube_audio(youtube_url, output_path):
    """Extract audio from YouTube video"""
    try:
        subprocess.run(
            ['yt-dlp', '-x', '--audio-format', 'mp3', '-o', output_path, youtube_url],
            check=True
        )
        return True
    except:
        return False

def process_video(video_path, audio_path, output_path, hdr_settings, fps, use_hdr):
    """Process video with audio and HDR effect"""
    
    # Get durations
    audio_duration = get_audio_duration(audio_path)
    video_duration = get_video_duration(video_path)
    
    if not audio_duration or not video_duration:
        return False, "Could not get media durations"
    
    # Calculate random start time for video
    if video_duration > audio_duration:
        max_start = video_duration - audio_duration
        start_time = random.uniform(0, max_start)
    else:
        start_time = 0
    
    # Build HDR filter
    hdr_filter = ""
    if use_hdr:
        size = hdr_settings['Size'] / 100
        amount = hdr_settings['Amount'] / 100
        strength = hdr_settings['Strength'] / 100
        filters = hdr_settings['Filters'] / 100
        glow = hdr_settings['Glow'] / 100
        range_val = hdr_settings['Range'] / 100
        
        # HDR effect using eq, vibrance, and unsharp filters
        hdr_filter = f"eq=contrast=1+{strength}:brightness={amount*0.1}:saturation=1+{filters},vibrance=intensity={glow},unsharp=5:5:{strength*3}:5:5:{strength*2},eq=gamma=1+{range_val*0.3}"
    
    # Build complete filter
    scale_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    if hdr_filter:
        complete_filter = f"{scale_filter},{hdr_filter}"
    else:
        complete_filter = scale_filter
    
    try:
        # FFmpeg command
        cmd = [
            'ffmpeg',
            '-ss', str(start_time),
            '-i', video_path,
            '-i', audio_path,
            '-t', str(audio_duration),
            '-vf', complete_filter,
            '-r', str(fps),
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',
            '-b:v', '8M',
            '-maxrate', '10M',
            '-bufsize', '16M',
            '-c:a', 'aac',
            '-b:a', '320k',
            '-map', '0:v:0',
            '-map', '1:a:0',
            '-shortest',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return True, "Success"
    except subprocess.CalledProcessError as e:
        return False, f"FFmpeg error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    fps = st.selectbox("Frame Rate", options=[30, 60], index=1, help="Select output video frame rate")
    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    st.markdown("[App](https://streamladder.com)", unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("### 🎧 Audio Source")
    audio_option = st.radio("Choose audio source", ["Upload Audio File", "YouTube Link"], label_visibility="collapsed")
    
    audio_file = None
    youtube_url = None
    
    if audio_option == "Upload Audio File":
        audio_file = st.file_uploader("Upload Audio (MP3, WAV, M4A)", type=['mp3', 'wav', 'm4a', 'aac'], help="Upload your audio file")
    else:
        youtube_url = st.text_input("YouTube URL", placeholder="https://youtube.com/watch?v...", help="Paste YouTube video URL to extract audio")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.markdown("### 🎥 Background Video")
    video_option = st.radio("Choose video source", ["Upload Video File", "Use Default Video"], label_visibility="collapsed")
    
    video_file = None
    use_default = False
    
    if video_option == "Upload Video File":
        video_file = st.file_uploader("Upload Video (MP4, MOV, AVI)", type=['mp4', 'mov', 'avi', 'mkv'], help="Upload your background video")
    else:
        use_default = True
        st.info("ℹ️ Using default video: D:\\0307 2.mp4")
    
    st.markdown('</div>', unsafe_allow_html=True)

# HDR Settings
st.markdown('<div class="effect-panel">', unsafe_allow_html=True)
st.markdown("### ✨ HDR Effect Settings")

use_hdr = st.checkbox("Enable HDR Effect", value=True)

if use_hdr:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        size = st.slider("Size", 0, 100, 70, help="Effect size")
        amount = st.slider("Amount", 0, 100, 5, help="Effect intensity")
    
    with col2:
        strength = st.slider("Strength", 0, 100, 75, help="Effect strength")
        filters = st.slider("Filters", 0, 100, 80, help="Color filters")
    
    with col3:
        glow = st.slider("Glow", 0, 100, 50, help="Glow effect")
        range_val = st.slider("Range", 0, 100, 23, help="Dynamic range")
    
    hdr_settings = {
        'Size': size,
        'Amount': amount,
        'Strength': strength,
        'Filters': filters,
        'Glow': glow,
        'Range': range_val
    }
else:
    hdr_settings = {
        'Size': 70,
        'Amount': 5,
        'Strength': 75,
        'Filters': 80,
        'Glow': 50,
        'Range': 23
    }

st.markdown('</div>', unsafe_allow_html=True)

# Process button
st.markdown("<br>", unsafe_allow_html=True)

if st.button("🎥 Process Video", use_container_width=True):
    # Validation
    if not audio_file and not youtube_url:
        st.error("❌ Please provide an audio source (upload file or YouTube URL)")
    elif not video_file and not use_default:
        st.error("❌ Please provide a video source (upload file or use default)")
    else:
        st.session_state.processing = True
        
        with st.spinner("🚀 Processing your video..."):
            # Create temp directory
            temp_dir = tempfile.mkdtemp()
            
            try:
                # Handle audio
                audio_path = None
                if audio_file:
                    audio_path = os.path.join(temp_dir, "audio.mp3")
                    with open(audio_path, "wb") as f:
                        f.write(audio_file.getbuffer())
                    st.success("✅ Audio uploaded")
                elif youtube_url:
                    audio_path = os.path.join(temp_dir, "audio.mp3")
                    st.info("📥 Extracting audio from YouTube...")
                    if extract_youtube_audio(youtube_url, audio_path):
                        st.success("✅ Audio extracted from YouTube")
                    else:
                        st.error("❌ Failed to extract audio from YouTube")
                        st.stop()
                
                # Handle video
                video_path = None
                if video_file:
                    video_path = os.path.join(temp_dir, "video.mp4")
                    with open(video_path, "wb") as f:
                        f.write(video_file.getbuffer())
                    st.success("✅ Video uploaded")
                elif use_default:
                    default_path = r"D:\0307 2.mp4"
                    if os.path.exists(default_path):
                        video_path = default_path
                        st.success("✅ Using default video")
                    else:
                        st.error(f"❌ Default video not found: {default_path}")
                        st.info("📝 Please upload a video file instead")
                        st.stop()
                
                # Process video
                output_path = os.path.join(temp_dir, "output.mp4")
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("⚙️ Processing video with HDR effects...")
                progress_bar.progress(50)
                
                success, message = process_video(
                    video_path, audio_path, output_path,
                    hdr_settings, fps, use_hdr
                )
                
                progress_bar.progress(100)
                
                if success:
                    status_text.text("✨ Video processed successfully!")
                    
                    # Read output file
                    with open(output_path, 'rb') as f:
                        video_bytes = f.read()
                    
                    # Download button
                    st.success("🎉 Your video is ready!")
                    st.download_button(
                        label="💾 Download Video",
                        data=video_bytes,
                        file_name="edited_video.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                    
                    # Preview
                    st.video(output_path)
                else:
                    status_text.text("")
                    st.error(f"❌ Processing failed: {message}")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            
            finally:
                # Cleanup
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
                st.session_state.processing = False

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666;">' 
    '<p>Made with ❤️ using Streamlit | High-quality video processing with HDR effects</p>' 
    '</div>',
    unsafe_allow_html=True
)
