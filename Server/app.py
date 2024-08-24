import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the YouTube Transcript API!"}), 200

@app.route("/get_transcript", methods=["GET"])
def get_transcript():
    video_id = request.args.get("video_id")
    if not video_id:
        return jsonify({"error": "Video ID is required"}), 400

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return jsonify({"transcript": transcript})
    except TranscriptsDisabled:
        logging.error(f"Transcripts are disabled for video_id: {video_id}")
        return jsonify({"error": "Transcripts are disabled for this video."}), 400
    except NoTranscriptFound:
        logging.error(f"No transcript found for video_id: {video_id}")
        return jsonify({"error": "No transcript found for this video."}), 404
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=10000)
