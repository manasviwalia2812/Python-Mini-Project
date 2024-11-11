from flask import Flask, render_template, request, jsonify
import ollama

app = Flask(__name__)

# Initialize conversation history
conversation_history = []

def chatbot_response(conversation_history, prompt):
    conversation_history.append({"role": "user", "content": prompt})
    response = ollama.chat(model="llama2", messages=conversation_history)
    conversation_history.append({"role": "assistant", "content": response['message']['content']})
    return response['message']['content']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json.get("user_input")
    if user_input:
        response = chatbot_response(conversation_history, user_input)
        return jsonify({"response": response})
    return jsonify({"response": "Sorry, something went wrong."})

if __name__ == "__main__":
    app.run(debug=True)
