import os
from pathlib import Path
from typing import Tuple

from PIL import Image
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
try:
    from moviepy.editor import TextClip
    _HAS_TEXTCLIP = True
except Exception:
    _HAS_TEXTCLIP = False

from ..config import AppConfig


def _tts_to_file(text: str, out_path: Path) -> Path:
    provider = AppConfig().TTS_PROVIDER
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if provider == 'gtts':
        from gtts import gTTS
        tts = gTTS(text=text)
        mp3_path = out_path.with_suffix('.mp3')
        tts.save(str(mp3_path))
        return mp3_path
    elif provider == 'elevenlabs' and AppConfig().ELEVENLABS_API_KEY:
        import requests
        headers = {
            'xi-api-key': AppConfig().ELEVENLABS_API_KEY,
        }
        payload = {
            'text': text,
            'voice_settings': {"stability": 0.4, "similarity_boost": 0.8}
        }
        resp = requests.post('https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM', json=payload, headers=headers)
        resp.raise_for_status()
        mp3_path = out_path.with_suffix('.mp3')
        with open(mp3_path, 'wb') as f:
            f.write(resp.content)
        return mp3_path
    else:
        # Fallback: simple beep (requires ffmpeg) - but try to still produce a file
        mp3_path = out_path.with_suffix('.mp3')
        with open(mp3_path, 'wb') as f:
            f.write(b'')
        return mp3_path


def _generate_with_veo(story_text: str, image_path: str) -> Tuple[str, str]:
    """Generate video using Google Veo via Vertex AI.
    Returns tuple of (local_video_path, public_url_or_local_route).
    """
    cfg = AppConfig()
    
    # Check if Veo is properly configured
    if not cfg.GCP_PROJECT_ID or not cfg.GOOGLE_APPLICATION_CREDENTIALS:
        raise RuntimeError("Veo not properly configured. GCP_PROJECT_ID and GOOGLE_APPLICATION_CREDENTIALS required.")
    
    # Lazy import to avoid dependency unless configured
    try:
        from vertexai.preview.vision_models import VideoGenerationModel
        import vertexai
    except ImportError:
        raise RuntimeError("Veo dependencies not available. Install google-cloud-aiplatform>=1.64.0")
    except Exception as e:
        raise RuntimeError(f"Veo initialization failed: {e}")

    # Initialize Vertex AI
    vertexai.init(project=cfg.GCP_PROJECT_ID, location=cfg.GCP_LOCATION)

    # Basic prompt combining story and hint about style
    prompt = f"Narrative: {story_text}\nGenerate a short 720p video suitable for gardening tips, with calm pacing."

    model = VideoGenerationModel.from_pretrained(cfg.VEO_MODEL_NAME)
    # Veo can accept image conditioning; pass the uploaded image as a reference frame
    try:
        result = model.generate(
            prompt=prompt,
            images=[image_path],
            output_mime_type="video/mp4",
            aspect_ratio="16:9",
            duration_seconds=10,
        )
    except Exception as e:
        raise RuntimeError(f"Veo generation failed: {e}")

    cfg_media = Path(cfg.MEDIA_DIR)
    cfg_media.mkdir(parents=True, exist_ok=True)
    out_path = cfg_media / f"veo_{Path(image_path).stem}.mp4"
    # result can be bytes or an object with .save; handle both
    try:
        if hasattr(result, 'save'):
            result.save(str(out_path))
        elif isinstance(result, (bytes, bytearray)):
            with open(out_path, 'wb') as f:
                f.write(result)
        else:
            # Fallback if result has .media or similar
            content = getattr(result, 'media', None)
            if content:
                with open(out_path, 'wb') as f:
                    f.write(content)
            else:
                raise RuntimeError('Unexpected Veo result type')
    except Exception as e:
        raise RuntimeError(f"Saving Veo output failed: {e}")

    public_url = f"/media/{out_path.name}"
    return str(out_path), public_url


def _generate_with_gemini(story_text: str, image_path: str) -> Tuple[str, str]:
    """Generate video using Gemini via Google AI Studio API.
    Returns tuple of (local_video_path, public_url_or_local_route).
    """
    cfg = AppConfig()
    if not cfg.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set for Gemini video generation")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=cfg.GEMINI_API_KEY)
        model = genai.GenerativeModel(cfg.GEMINI_VIDEO_MODEL)
    except ImportError:
        raise RuntimeError("Gemini dependencies not available. Install google-generativeai")
    except Exception as e:
        raise RuntimeError(f"Gemini initialization failed: {e}")

    # Create a video generation prompt
    prompt = f"""
    Create a short educational video about soil health based on this story:
    
    {story_text}
    
    The video should be:
    - 10-15 seconds long
    - Educational and informative
    - Suitable for gardeners
    - Include visual elements related to soil, plants, and gardening
    - Have a calm, professional tone
    """
    
    try:
        # Generate video using Gemini
        response = model.generate_content(prompt)
        
        # Handle video response (may be bytes or a file-like object)
        if hasattr(response, 'video'):
            video_data = response.video
        elif hasattr(response, 'parts') and response.parts:
            # Try to extract video from parts
            for part in response.parts:
                if hasattr(part, 'video'):
                    video_data = part.video
                    break
            else:
                raise RuntimeError("No video found in Gemini response")
        else:
            raise RuntimeError("Unexpected Gemini response format")
        
        # Save video to local storage
        cfg_media = Path(cfg.MEDIA_DIR)
        cfg_media.mkdir(parents=True, exist_ok=True)
        out_path = cfg_media / f"gemini_{Path(image_path).stem}.mp4"
        
        if isinstance(video_data, bytes):
            with open(out_path, 'wb') as f:
                f.write(video_data)
        else:
            # If it's a file-like object
            with open(out_path, 'wb') as f:
                f.write(video_data.read())
        
        public_url = f"/media/{out_path.name}"
        return str(out_path), public_url
        
    except Exception as e:
        raise RuntimeError(f"Gemini video generation failed: {e}")


def _generate_local_video(story_text: str, image_path: str) -> Tuple[str, str]:
    """Generate video using local TTS + moviepy method.
    Returns tuple of (local_video_path, public_url_or_local_route).
    """
    cfg = AppConfig()
    media_dir = Path(cfg.MEDIA_DIR)
    media_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"story_{os.path.splitext(os.path.basename(image_path))[0]}"
    audio_path = media_dir / f"{base_name}_audio"
    audio_file = _tts_to_file(story_text, audio_path)

    # Build simple video: static image with audio; add captions as overlay text
    img_clip = ImageClip(image_path).set_duration(max(6, len(story_text.split()) / 2.5))
    narration = AudioFileClip(str(audio_file)) if os.path.getsize(audio_file) > 0 else None
    if narration:
        img_clip = img_clip.set_audio(narration)

    layers = [img_clip]
    if _HAS_TEXTCLIP:
        try:
            caption = TextClip(story_text, fontsize=32, color='white', method='caption', align='West', size=(img_clip.w - 100, None))
            caption = caption.set_duration(img_clip.duration).set_position((50, img_clip.h*0.65))
            layers.append(caption)
        except Exception:
            pass

    final = CompositeVideoClip(layers)
    video_path = media_dir / f"{base_name}.mp4"
    final.write_videofile(str(video_path), fps=24)

    public_url = f"/media/{video_path.name}"
    return str(video_path), public_url


def generate_story_video(story_text: str, image_path: str) -> Tuple[str, str]:
    """Generate a story video using the configured provider.
    Returns tuple of (local_video_path, public_url_or_local_route).
    """
    cfg = AppConfig()
    provider = cfg.VIDEO_PROVIDER.lower() if cfg.VIDEO_PROVIDER else 'gemini'
    
    print(f"🎬 Generating video with provider: {provider}")
    
    try:
        # Try Gemini first (default and most reliable)
        if provider in ['gemini', 'default', '']:
            print("🎬 Attempting Gemini video generation...")
            return _generate_with_gemini(story_text, image_path)
        
        # Try Veo if specifically requested and configured
        elif provider == 'veo':
            print("🎬 Attempting Veo video generation...")
            return _generate_with_veo(story_text, image_path)
        
        # Fallback to local generation
        elif provider == 'local':
            print("🎬 Using local video generation...")
            return _generate_local_video(story_text, image_path)
        
        # Unknown provider, fallback to Gemini
        else:
            print(f"🎬 Unknown provider '{provider}', falling back to Gemini...")
            return _generate_with_gemini(story_text, image_path)
            
    except Exception as e:
        print(f"⚠️  Video generation with {provider} failed: {e}")
        
        # Fallback chain: try other providers if the primary one fails
        if provider != 'local':
            try:
                print("🔄 Falling back to local video generation...")
                return _generate_local_video(story_text, image_path)
            except Exception as local_error:
                print(f"❌ Local video generation also failed: {local_error}")
                raise RuntimeError(f"All video generation methods failed. Last error: {local_error}")
        else:
            raise RuntimeError(f"Video generation failed: {e}")


