import sys
from google.cloud import aiplatform as vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project="project-743aab84-f9a5-4ec7-954", location="us-central1")

models_to_test = ["gemini-1.5-flash", "gemini-1.5-flash-002", "gemini-1.5-flash-001"]

for model_name in models_to_test:
    print(f"\nTrying model: {model_name}...")
    try:
        model = GenerativeModel(model_name)
        response = model.generate_content("Test connection: confirm project billing access.")
        print(f"SUCCESS with {model_name}!")
        print("Response text:", response.text.strip())
        break
    except Exception as e:
        print(f"FAILED with {model_name}: {type(e).__name__} - {e}")
