import os
from llama_cpp import Llama
import time

def load_model():
    """
    Load the Llama model.
    You need to download the model file first and place it in the same directory.
    """
    try:
        # Initialize the model
        # You can download models from: https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF
        model_path = "llama-2-7b-chat.Q4_K_M.gguf"  # Update this with your model file name
        llm = Llama(
            model_path=model_path,
            n_ctx=2048,  # Context window
            n_threads=4   # Number of CPU threads to use
        )
        return llm
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def summarize_text(text, llm):
    """
    Summarize the given text using Llama model.
    """
    try:
        # Create the prompt
        prompt = f"""Please summarize the following medical text in simple, easy-to-understand language:

{text}

Summary:"""

        # Generate the summary
        start_time = time.time()
        response = llm(
            prompt,
            max_tokens=512,
            temperature=0.7,
            stop=["Summary:", "\n\n"],
            echo=False
        )
        end_time = time.time()

        # Extract the generated text
        summary = response['choices'][0]['text'].strip()
        processing_time = end_time - start_time

        return {
            'summary': summary,
            'processing_time': f"{processing_time:.2f} seconds"
        }

    except Exception as e:
        return {
            'error': f"Error generating summary: {str(e)}"
        }

def main():
    # Load the model
    print("Loading Llama model...")
    llm = load_model()
    
    if llm is None:
        print("Failed to load model. Please make sure you have downloaded the model file.")
        return

    print("Model loaded successfully!")
    print("\nEnter your medical text (press Ctrl+D or Ctrl+Z when done):")
    
    # Get input text
    text_lines = []
    try:
        while True:
            line = input()
            text_lines.append(line)
    except EOFError:
        text = "\n".join(text_lines)

    if not text.strip():
        print("No text provided.")
        return

    # Generate summary
    print("\nGenerating summary...")
    result = summarize_text(text, llm)

    if 'error' in result:
        print(result['error'])
    else:
        print("\nSummary:")
        print("-" * 50)
        print(result['summary'])
        print("-" * 50)
        print(f"\nProcessing time: {result['processing_time']}")

if __name__ == "__main__":
    main() 