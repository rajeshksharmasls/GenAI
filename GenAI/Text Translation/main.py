from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import T5ForConditionalGeneration, T5Tokenizer

TF_ENABLE_ONEDNN_OPTS = 0 # Turn off oneDNN optimizations for more consistent floating-point results
TF_CPP_MIN_LOG_LEVEL = 1  # Suppress TensorFlow logs for cleaner output 

# Initialize FastAPI app
app = FastAPI()

# Load the pre-trained T5-small model and tokenizer from Hugging Face
model_name = "google-t5/t5-small"
model = T5ForConditionalGeneration.from_pretrained(model_name)
tokenizer = T5Tokenizer.from_pretrained(model_name, legacy=False)

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

# Define the translation function
def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    input_text = f"translate {source_lang} to {target_lang}: {text}"
    inputs = tokenizer(input_text, return_tensors="pt", padding=True)
    outputs = model.generate(**inputs, max_new_tokens=50)
    translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return translated_text

# Create a POST endpoint for translation
@app.post("/translate/")
async def translate(request: TranslationRequest):
    try:
        translated_text = translate_text(request.text, request.source_lang, request.target_lang)
        return {"original": request.text, "translated": translated_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
