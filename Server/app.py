import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi, YouTubeTranscriptApiFetcher
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import requests

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

logging.basicConfig(level=logging.INFO)

# Custom headers to mimic a real browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.youtube.com/',
}

# Override the _fetch_transcripts method to include headers
class CustomYouTubeTranscriptApiFetcher(YouTubeTranscriptApiFetcher):
    def _fetch_transcripts(self, video_id, languages):
        url = f"https://www.youtube.com/api/timedtext?type=list&v={video_id}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return self._parse_transcripts(response.text)

# Use the custom fetcher
YouTubeTranscriptApi.fetcher = CustomYouTubeTranscriptApiFetcher()

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
