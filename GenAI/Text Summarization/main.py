from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import T5Tokenizer, T5ForConditionalGeneration

MODEL_NAME = "t5-small"
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)

# Initialize FastAPI
app = FastAPI(title="Text Summarization API", version = "1.0")

# Pydantic model for input validation
class StoryRequest(BaseModel):
    Story: str

# POST endpoint for generating a story based on the title
@app.post("/Summarize")
async def generate_story(request: StoryRequest):
    # Get the title from the request
    Story = request.Story

    #Validate the input text
    if (len(Story) == 0):
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    
    #Preprocess the input
    input_text = f"Please summarize the following text:\n\n{Story}"

    input_ids = tokenizer.encode(input_text, return_tensors="pt",
    max_length=512, truncation=True)

    # Generate summary
    response = model.generate(input_ids,max_length=50)
        
    #Decode Summary
    summary = tokenizer.decode(response[0], skip_special_tokens=True)

    # Return the generated story as a response
    return {"Story": Story, "Summmary": summary}

@app.get("/")
async def root():
    return {"message": "Welcome to the Text Summarization API!"}