import ollama
import json
import logging


# Logging configuration
# logging.basicConfig(filename='chatbot.log', level=logging.INFO)


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
        with open(filename, "w", encoding="utf-8") as file:  # Specify UTF-8 encoding
            for message in self.history:
                file.write(f"{message['role'].capitalize()}: {message['content']}\n")


    def delete_history(self):
        """Delete the conversation history"""
        self.history = []  # Clear the in-memory history


# UserProfile class to handle user-related data (e.g., name, preferences)
class UserProfile:
    def __init__(self, user_id, name=None, preferences=None):
        self.user_id = user_id
        self.name = name or "Guest"
        self.preferences = preferences or {}

    def greet_user(self):
        """Return a greeting message"""
        return f"Hello, {self.name}!"

    def update_preferences(self, new_preferences):
        """Update user preferences"""
        self.preferences.update(new_preferences)

    def display_preferences(self):
        """Display current preferences"""
        if not self.preferences:
            return "No preferences set."
        return "Current preferences:\n" + "\n".join(f"{key}: {value}" for key, value in self.preferences.items())


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
            bot_response = response['message']['content']
            logging.info(f"Bot: {bot_response}")
            self.conversation_history.add_message("assistant", bot_response)
            self.conversation_history.save_history(self.history_file)
            return bot_response
        except Exception as e:
            logging.error(f"Error during chatbot response: {str(e)}")
            return "Sorry, something went wrong while getting a response."

    def display_menu(self):
        """Display menu options to the user"""
        print("\nMenu:")
        print("1. Send a message")
        print("2. View conversation history")
        print("3. Export conversation history")
        print("4. Delete conversation history")
        print("5. Update user profile")
        print("6. View current preferences")
        print("7. Exit")

    def handle_menu_option(self, option):
      """Handle menu options"""
      if option == "1":
          user_input = input("You: ")
          response = self.send_message(user_input)
          print(f"Bot: {response}")
      elif option == "2":
          print("\nConversation History:")
          for message in self.conversation_history.history:
              print(f"{message['role'].capitalize()}: {message['content']}")
      elif option == "3":
          file_type = input("Enter file type (json/txt): ").strip().lower()
          if file_type == "json":
              self.conversation_history.save_history()
              print("Conversation history saved as JSON.")
          elif file_type == "txt":
              self.conversation_history.export_history()
              print("Conversation history exported as TXT.")
          else:
              print("Invalid file type.")
      elif option == "4":
          self.conversation_history.delete_history()
          print("Conversation history deleted.")
      elif option == "5":
          name = input("Enter your name: ").strip()
          preferences = input("Enter preferences (key=value pairs, comma-separated): ")
          prefs_dict = dict(pref.split("=") for pref in preferences.split(",") if "=" in pref)
          self.user_profile.name = name
          self.user_profile.update_preferences(prefs_dict)
          print(f"Profile updated. Welcome, {self.user_profile.name}!")
          print(self.user_profile.display_preferences())  # Show updated preferences
      elif option == "6":
          print(self.user_profile.display_preferences())  # Add option to display preferences
      elif option == "7":
          print("Goodbye!")
          return False
      else:
          print("Invalid option. Please try again.")
      return True


def main():
    user_profile = UserProfile(user_id="guest", name="Guest")
    chatbot = Chatbot(user_profile=user_profile)
    print(user_profile.greet_user())

    running = True
    while running:
        chatbot.display_menu()
        option = input("Choose an option: ").strip()
        running = chatbot.handle_menu_option(option)


if __name__ == "__main__":
    main()
