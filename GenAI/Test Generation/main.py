from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM

# Initialize FastAPI
app = FastAPI(title="Text Generation API with Qwen", version="1.0")

# Load the StableLM model and tokenizer
MODEL_NAME = "Qwen/Qwen2.5-0.5B"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# Set the pad token ID (necessary if the tokenizer lacks it)
if tokenizer.pad_token_id is None:
    tokenizer.pad_token_id = tokenizer.eos_token_id

# Pydantic model for input validation
class StoryRequest(BaseModel):
    title: str

# Pydantic model for response validation
class StoryResponse(BaseModel):
    title: str
    story: str

@app.post("/story", response_model=StoryResponse)
async def generate_story(request: StoryRequest):
    title = request.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    # Create a prompt for story generation
    prompt = f"Write a short story about {title}."
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)

    # Generate text
    outputs = model.generate(
        inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=200,  # Avoid using `max_length` if `max_new_tokens` is set
        temperature=0.7,
        top_k=50,
        top_p=0.9,
        do_sample=True
    )

    story = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Return the generated story
    return {"title": title, "story": story}
