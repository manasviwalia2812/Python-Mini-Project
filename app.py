from flask import Flask, render_template, request, jsonify, send_file
import ollama
import json
import logging

app = Flask(__name__)

# Logging configuration
logging.basicConfig(filename='chatbot.log', level=logging.INFO)

# ConversationHistory class to handle saving/loading conversation history
class ConversationHistory:
    def __init__(self):
        self.history = []

    def add_message(self, role, message):
        """Add a message to the conversation history"""
        self.history.append({"role": role, "content": message})

    def save_history(self, filename="conversation_history.json"):
        """Save the conversation history to a file"""
        with open(filename, "w") as file:
            json.dump(self.history, file)

    def load_history(self, filename="conversation_history.json"):
        """Load the conversation history from a file"""
        try:
            with open(filename, "r") as file:
                self.history = json.load(file)
        except FileNotFoundError:
            self.history = []

    def export_history(self, filename="conversation_history.txt"):
        """Export the conversation history as a text file"""
        with open(filename, "w") as file:
            for message in self.history:
                file.write(f"{message['role'].capitalize()}: {message['content']}\n")
    
    def delete_history(self, filename="conversation_history.json"):
        """Delete the conversation history"""
        self.history = []  # Clear the in-memory history
        with open(filename, "w") as file:
            json.dump(self.history, file)  # Save an empty history file

# UserProfile class to handle user-related data (e.g., name, preferences)
class UserProfile:
    def __init__(self, user_id, name=None, preferences=None):
        self.user_id = user_id
        self.name = name or "Guest"
        self.preferences = preferences or {}

    def update_preferences(self, new_preferences):
        """Update user preferences"""
        self.preferences.update(new_preferences)

    def greet_user(self):
        """Return a greeting message"""
        return f"Hello, {self.name}!"

    def update_profile(self, name=None, preferences=None):
        """Update user's name or preferences"""
        if name:
            self.name = name
        if preferences:
            self.preferences.update(preferences)

# Chatbot class to encapsulate chatbot logic
class Chatbot:
    def __init__(self, model="llama2", user_profile=None, history_file="conversation_history.json"):
        self.model = model
        self.conversation_history = ConversationHistory()
        self.history_file = history_file
        self.conversation_history.load_history(self.history_file)
        self.user_profile = user_profile or UserProfile(user_id="guest")

    def send_message(self, message):
        """Send a message to the chatbot and get a response"""
        logging.info(f"User: {message}")
        self.conversation_history.add_message("user", message)
        try:
            # Fetch the response from Ollama model
            response = ollama.chat(model=self.model, messages=self.conversation_history.history)
            logging.info(f"Bot: {response['message']['content']}")
            self.conversation_history.add_message("assistant", response['message']['content'])
            self.conversation_history.save_history(self.history_file)
            return response['message']['content']
        except Exception as e:
            logging.error(f"Error during chatbot response: {str(e)}")
            return "Sorry, something went wrong while getting a response."

# Flask routes
@app.route('/')
def home():
    """Render the homepage"""
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    """Handle user input and return chatbot response"""
    user_input = request.json.get("user_input")
    if user_input:
        chatbot = Chatbot()  # Instantiate the chatbot
        response = chatbot.send_message(user_input)
        return jsonify({"response": response})
    return jsonify({"response": "Sorry, something went wrong."})

@app.route('/download_history', methods=['GET'])
def download_history():
    """Route to download the conversation history as a file"""
    file_type = request.args.get('file_type', 'json')  # Default to JSON
    chatbot = Chatbot()  # Instantiate the chatbot (or use the existing instance)
    if file_type == 'json':
        history_filename = "conversation_history.json"
        chatbot.conversation_history.save_history(history_filename)  # Save current history
        return send_file(history_filename, as_attachment=True)
    else:
        history_filename = "conversation_history.txt"
        chatbot.conversation_history.export_history(history_filename)  # Export to text file
        return send_file(history_filename, as_attachment=True)

@app.route('/delete_history', methods=['POST'])
def delete_history():
    """Handle request to delete the conversation history"""
    chatbot = Chatbot()  # Instantiate the chatbot
    chatbot.conversation_history.delete_history()  # Clear the history
    return jsonify({"response": "Conversation history deleted."})

@app.route('/update_profile', methods=['POST'])
def update_profile():
    """Handle request to update user profile"""
    user_id = request.json.get("user_id")
    name = request.json.get("name")
    preferences = request.json.get("preferences")
    
    # Create or update user profile
    user_profile = UserProfile(user_id=user_id, name=name, preferences=preferences)
    return jsonify({
        "response": f"Profile updated for {user_profile.name}."
    })



if __name__ == "__main__":
    app.run(debug=True)
