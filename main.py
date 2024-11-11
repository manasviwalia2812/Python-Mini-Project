import ollama

def chatbot_response(conversation_history, prompt):
    conversation_history.append({"role": "user", "content": prompt})
    response = ollama.chat(model="llama2", messages=conversation_history)
    print(response)  # This will help you inspect the response structure
    conversation_history.append({"role": "assistant", "content": response['message']['content']})
    return response['message']['content'], conversation_history

# Initialize conversation history
conversation_history = []

while True:
    user_input = input("You: Type 'exit' to quit ")
    if user_input.lower() == 'exit':
        break
    response, conversation_history = chatbot_response(conversation_history, user_input)
    print("AI:", response)
