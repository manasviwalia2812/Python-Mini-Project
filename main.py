import openai

openai.api_key = "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"

def chat_with_gpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content'].strip()

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("AI: Goodbye!")
            break
        
        response = chat_with_gpt(user_input)
        print("AI:", response)
