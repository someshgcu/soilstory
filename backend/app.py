import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, render_template
from werkzeug.utils import secure_filename

from .config import AppConfig
from .services.auth import require_firebase_auth
from .services.db import db_create_analysis, db_get_user_history, db_get_analysis, db_update_analysis_video
from .services.weather import fetch_weather_snapshot
from .services.story import generate_soil_story
from .services.video import generate_story_video
from .ml.soil_analyzer import analyze_image_bytes


def create_app() -> Flask:
    # Load environment variables from .env if present
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).resolve().parents[1] / 'frontend' / 'templates'),
        static_folder=str(Path(__file__).resolve().parents[1] / 'frontend' / 'static'),
        static_url_path='/static'
    )
    app.config.from_object(AppConfig())

    uploads_dir = Path(app.config['UPLOADS_DIR'])
    media_dir = Path(app.config['MEDIA_DIR'])
    uploads_dir.mkdir(parents=True, exist_ok=True)
    media_dir.mkdir(parents=True, exist_ok=True)

    @app.get('/health')
    def health():
        return jsonify({"status": "ok"})

    @app.get('/')
    def index():
        return render_template('index.html')

    @app.get('/history')
    def history_page():
        return render_template('history.html')

    @app.post('/api/analyze')
    @require_firebase_auth
    def api_analyze(user):
        try:
            # Accept either file upload or base64 in JSON
            if 'photo' in request.files:
                image_file = request.files['photo']
                filename = secure_filename(image_file.filename) or f"soil_{uuid.uuid4().hex}.jpg"
                saved_path = uploads_dir / filename
                image_file.save(saved_path)
                with open(saved_path, 'rb') as f:
                    image_bytes = f.read()
            else:
                payload = request.get_json(silent=True) or {}
                b64_data = payload.get('imageBase64')
                if not b64_data:
                    return jsonify({"error": "No image provided"}), 400
                import base64
                image_bytes = base64.b64decode(b64_data.split(',')[-1])
                filename = f"soil_{uuid.uuid4().hex}.jpg"
                saved_path = uploads_dir / filename
                with open(saved_path, 'wb') as f:
                    f.write(image_bytes)

            # Location
            lat = request.form.get('lat') or (request.get_json(silent=True) or {}).get('lat')
            lon = request.form.get('lon') or (request.get_json(silent=True) or {}).get('lon')
            if lat is not None and lon is not None:
                try:
                    lat = float(lat)
                    lon = float(lon)
                except Exception:
                    return jsonify({"error": "Invalid lat/lon"}), 400
            else:
                lat = None
                lon = None

            # ML analysis
            analysis = analyze_image_bytes(image_bytes)

            # Weather snapshot
            weather = None
            if lat is not None and lon is not None:
                weather = fetch_weather_snapshot(lat, lon)

            # AI story
            story_text = generate_soil_story(analysis=analysis, weather=weather, location={"lat": lat, "lon": lon})

            # Persist to local storage
            record = {
                "userId": user["uid"],
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "imagePath": str(saved_path.as_posix()),
                "location": {"lat": lat, "lon": lon} if lat is not None and lon is not None else None,
                "analysis": analysis,
                "weather": weather,
                "story": story_text,
            }
            doc_id = db_create_analysis(record)

            return jsonify({
                "id": doc_id,
                "imagePath": record["imagePath"],
                "analysis": analysis,
                "weather": weather,
                "story": story_text,
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.post('/api/video')
    @require_firebase_auth
    def api_video(user):
        try:
            data = request.get_json(force=True)
            analysis_id = data.get('analysisId')
            if not analysis_id:
                return jsonify({"error": "analysisId is required"}), 400

            doc = db_get_analysis(analysis_id)
            if not doc:
                return jsonify({"error": "Analysis not found"}), 404
            if doc.get('userId') != user['uid']:
                return jsonify({"error": "Forbidden"}), 403

            image_path = doc.get('imagePath')
            story_text = doc.get('story')
            if not image_path or not story_text:
                return jsonify({"error": "Record missing image or story"}), 400

            video_path, public_url = generate_story_video(story_text=story_text, image_path=image_path)

            db_update_analysis_video(analysis_id, {
                "videoPath": video_path,
                "videoUrl": public_url,
            })

            return jsonify({
                "videoPath": video_path,
                "videoUrl": public_url,
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.get('/api/history')
    @require_firebase_auth
    def api_history(user):
        try:
            items = db_get_user_history(user['uid'])
            return jsonify({"items": items})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Serve saved media if using local storage
    @app.get('/media/<path:filename>')
    def serve_media(filename):
        return send_from_directory(media_dir, filename, as_attachment=False)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)


