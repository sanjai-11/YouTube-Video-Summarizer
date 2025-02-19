from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api import TranscriptsDisabled
import google.generativeai as genai
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables
def configure():
    load_dotenv()

configure()

def get_video_id(video_url):
    return video_url.split("watch?v=")[-1]

# Function to extract transcript
def extract_transcript(youtube_url):
    print("Extracting transcript...")
    video_id = get_video_id(youtube_url)
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = ' '.join([r['text'] for r in transcript])
        print("Transcript collected successfully.")
        return transcript_text
    
    except TranscriptsDisabled:
        print(f"Transcripts are disabled for video ID: {video_id}")
        return f"Transcripts are disabled for video ID: {video_id}"
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"An error occurred: {e}"

# Function to summarize the transcript
def summarize_content(transcript):
    print("Summarizing transcript...")
    prompt = f"Summarize this YouTube video transcript in a well-formatted way with proper punctuation in less than 200 words:\n\n{transcript}"
    genai.configure(api_key=os.getenv('API_KEY'))  # Ensure API key is set
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(contents=prompt)
    print("Summary generated successfully.")
    return response.text

@app.route('/', methods=['GET', 'POST'])
def home():
    summary = None
    if request.method == 'POST':
        youtube_url = request.form['youtubeLink']
        if youtube_url:
            print("Processing YouTube URL...")
            transcript = extract_transcript(youtube_url)
            summary = summarize_content(transcript)
        else:
            summary = "Error: No YouTube link provided or the link is not working."
    
    return render_template('index.html', summary=summary)

if __name__ == '__main__':
    app.run(debug=True)
