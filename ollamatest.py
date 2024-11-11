# test_ollama.py
import ollama

def test_ollama():
    try:
        # A simple test for the model
        prompt = "Hello, how are you?"
        response = ollama.chat(model="llama2", messages=[{"role": "user", "content": prompt}])
        print("Response:", response)
        if 'message' in response and 'content' in response['message']:
            print("Message from bot:", response['message']['content'])
        else:
            print("Error: Response does not contain 'content'.")
    except Exception as e:
        print("Error:", e)

test_ollama()
