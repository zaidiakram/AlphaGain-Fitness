from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser



load_dotenv()

model= GoogleGenerativeAI(model="gemini-2.0-flash")

result=model.invoke("what is the capital of india")

print(result)

