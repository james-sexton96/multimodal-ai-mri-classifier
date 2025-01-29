import base64
from io import BytesIO
from typing import List

from PIL import Image
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from langchain_ollama import OllamaLLM
from pydantic import BaseModel

from sys_temp import chat_prompt

app = FastAPI()

model = OllamaLLM(model="llama3.2-vision")
chain = chat_prompt | model

class PromptRequest(BaseModel):
    prompt: str

class Response(BaseModel):
    output: str

def encode_image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()

    # Get the format of the image or default to PNG
    image_format = image.format if image.format else 'PNG'
    image.save(buffered, format=image_format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@app.post("/generate_text", response_model=Response)
async def generate_text(request: PromptRequest):
    try:
        output = chain.invoke({"question": request.prompt})
        return {"output": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_multimodal", response_model=Response)
async def generate_multimodal(prompt: str = Form(...), images: List[UploadFile] = File(...)):
    try:
        content = [{"type": "text", "text": prompt}]
        for image_file in images:
            image = Image.open(image_file.file)
            image_base64 = encode_image_to_base64(image)
            content.append({
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{image_base64}",
                "b64": image_base64
            })

        # message = HumanMessage(content=content)
        llm_with_image_context = model.bind(images=[content[1]['b64']])
        # response = model.invoke([message])
        response = llm_with_image_context.invoke([content[0]['text']])
        return {"output": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

