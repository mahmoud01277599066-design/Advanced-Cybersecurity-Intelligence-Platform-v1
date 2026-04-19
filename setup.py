from setuptools import setup, find_packages

setup(
    name="acip-devsecops",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "langchain",
        "langchain-ollama",
        "langgraph",
        "pydantic",
        "python-dotenv",
        "chromadb",
        "fastapi",
        "uvicorn",
        "websockets",
    ],
)