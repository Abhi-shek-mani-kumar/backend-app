from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from pypdf import PdfReader
from io import BytesIO
from pydantic import BaseModel
import os
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")


app = FastAPI()
file_text = ""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global file_text

    pdf_bytes = await file.read()

    reader = PdfReader(BytesIO(pdf_bytes))

    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    file_text = text
    print(file_text)
    return {
        "message": "PDF uploaded successfully",
        "characters": len(file_text)
    }



class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(data: QuestionRequest):

    prompt = f"""
Answer the question based on the document.

Return plain text only.
Do not use markdown.
Do not use **, *, #, or bullet formatting.

Question:
{data.question}

Document:
{file_text}
"""

    response = model.generate_content(prompt)

    return {
        "answer": response.text
    }