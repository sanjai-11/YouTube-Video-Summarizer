from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import TranscriptsDisabled
import google.generativeai as genai
from dotenv import load_dotenv
import os

app = Flask(__name__)

def configure():
    load_dotenv()

def get_video_id(video_url):
    return video_url.split("watch?v=")[-1]

o
def extract_transcript(youtube_url):
    print("getting into extract_transcript()")
    video_id = get_video_id(youtube_url)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ''.join([r['text'] for r in transcript])
        print("trascript collected")
        return transcript
    
    except TranscriptsDisabled:
        print(f"Transcripts are disabled for video ID: {video_id}")
        return f"Transcripts are disabled for video ID: {video_id}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"


# Function to summarize the video transcript or content
def summarize_content(transcript):
    print("getting into summarize_content()")
    prompt = f"Summarize this youtube video transcript in good format with good punctuations in less than 200 words: \ntext = {transcript}"
    genai.configure(api_key=os.getenv('api'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(contents=prompt)
    print("summarized")
    return response.text

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        youtube_url = request.form['youtubeLink']
        if youtube_url:
            print("Collected YT url")
            transcript = extract_transcript(youtube_url)
            summary = summarize_content(transcript)
            return jsonify({"summary": summary})  # Return summary as JSON
        else:
            return jsonify({"error": "No YouTube link provided or Link is not working"}), 400
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)