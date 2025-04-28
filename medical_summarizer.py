from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

class MedicalRecordSummarizer:
    def __init__(self):
        # Initialize the model and tokenizer
        self.model_name = "facebook/bart-large-cnn"  # Using BART for summarization
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

        # Initialize the summarization pipeline
        self.summarizer = pipeline(
            "summarization",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1
        )

    def summarize(self, medical_text, max_length=150, min_length=50):
        """
        Summarize the medical record text
        """
        try:
            chunks = self._chunk_text(medical_text)
            summaries = []

            for chunk in chunks:
                summary = self.summarizer(
                    chunk,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                summaries.append(summary[0]['summary_text'])

            return " ".join(summaries)

        except Exception as e:
            return f"Error during summarization: {str(e)}"

    def _chunk_text(self, text, max_chunk_length=1024):
        """
        Split text into chunks that fit within the model's token limit
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            current_length += len(self.tokenizer.tokenize(word)) + 1
            if current_length > max_chunk_length:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(self.tokenizer.tokenize(word))
            else:
                current_chunk.append(word)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

summarizer = MedicalRecordSummarizer()

medical_record =  medical_record = """
    Patient Name: John Doe
    Age: 45
    Gender: Male
    Date of Visit: 2024-04-16
    
    Chief Complaint: Patient presents with persistent cough and shortness of breath for the past 2 weeks.
    
    History of Present Illness: The patient reports developing a dry cough approximately 2 weeks ago, which has progressively worsened. 
    He has been experiencing shortness of breath, particularly during physical activity. No fever or chills reported. 
    The patient denies any recent travel or exposure to sick contacts.
    
    Past Medical History: 
    - Hypertension (controlled with medication)
    - Type 2 Diabetes Mellitus
    - Hyperlipidemia
    
    Medications:
    - Lisinopril 10mg daily
    - Metformin 500mg twice daily
    - Atorvastatin 20mg daily
    
    Physical Examination:
    - Blood Pressure: 130/80 mmHg
    - Heart Rate: 78 bpm
    - Respiratory Rate: 18 breaths/min
    - Temperature: 98.6°F
    - Oxygen Saturation: 96% on room air
    
    Assessment: 
    - Acute bronchitis
    - Well-controlled hypertension
    - Well-controlled diabetes
    
    Plan:
    1. Prescribe cough suppressant
    2. Recommend rest and increased fluid intake
    3. Follow-up in 1 week if symptoms persist
    4. Continue current medications
    """

summary = summarizer.summarize(medical_record)
print(summary)