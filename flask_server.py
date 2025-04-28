# Install required packages
!pip install flask flask-cors transformers torch pyngrok

from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqGeneration
import torch
from pyngrok import ngrok
import time

app = Flask(__name__)
CORS(app)

# Initialize the model
print("Loading model...")
model_name = "facebook/bart-large-cnn"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqGeneration.from_pretrained(model_name)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)
print("Model loaded successfully!")

def chunk_text(text, max_chunk_length=1024):
    """Split text into chunks that fit within the model's token limit"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_length += len(tokenizer.tokenize(word)) + 1  # +1 for space
        if current_length > max_chunk_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(tokenizer.tokenize(word))
        else:
            current_chunk.append(word)
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        medical_text = data.get('medical_text', '')
        
        if not medical_text:
            return jsonify({'error': 'No medical text provided'}), 400
        
        # Split text into chunks if it's too long
        chunks = chunk_text(medical_text)
        summaries = []
        
        for chunk in chunks:
            summary = summarizer(
                chunk,
                max_length=150,
                min_length=50,
                do_sample=False
            )
            summaries.append(summary[0]['summary_text'])
        
        # Combine all summaries
        final_summary = " ".join(summaries)
        
        return jsonify({
            'summary': final_summary,
            'status': 'success',
            'processing_time': f"{time.time() - request.json.get('start_time', time.time())} seconds"
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'model_loaded': True,
        'gpu_available': torch.cuda.is_available()
    })

# Start ngrok tunnel
public_url = ngrok.connect(5000).public_url
print(f' * ngrok tunnel "{public_url}" -> "http://127.0.0.1:5000"')
print(f' * Use this URL in your HTML file: {public_url}/summarize')

# Run Flask app
app.run() 