# main.py

# Import necessary libraries
from tkinter import *
import pandas as pd
import random

# --------------------------- CONSTANTS --------------------------- #
# Define constants for colors and file paths for easy modification.
BACKGROUND_COLOR = "#B1DDC6"
DATA_FILE = "data/german_words.csv"  # The original, complete list of words.
PROGRESS_FILE = "data/words_to_learn.csv"  # A file to store words the user still needs to learn.

# --------------------------- LOAD DATA --------------------------- #
# This block handles loading the word data. It prioritizes loading the user's progress.

try:
    # Attempt to read from the progress file first.
    data = pd.read_csv(PROGRESS_FILE)
    # If the progress file is empty (e.g., after completing all words), raise an error to load the original file.
    if data.empty:
        raise FileNotFoundError
except (FileNotFoundError, pd.errors.EmptyDataError):
    # If the progress file doesn't exist or is empty, load the full list from the original CSV.
    data = pd.read_csv(DATA_FILE)
    # Save this full list to the progress file to start a new session.
    data.to_csv(PROGRESS_FILE, index=False)

# Convert the DataFrame into a list of dictionaries (e.g., [{'German': 'Wort', 'English': 'Word'}, ...]).
# This format is easier to work with for picking random words.
to_learn = data.to_dict(orient="records")
current_card = {}  # A global dictionary to hold the current flashcard's data.


# --------------------------- FUNCTIONS --------------------------- #

def next_card():
    """
    Displays a new random German word on the flashcard.
    If all words are learned, it shows a completion message and disables the buttons.
    """
    global current_card, flip_timer
    
    # First, cancel any existing timer to prevent the card from flipping prematurely.
    window.after_cancel(flip_timer)

    # Check if there are any words left to learn.
    if not to_learn:
        # If the list is empty, display a completion message.
        canvas.itemconfig(card_title, text="Well Done!", fill="black")
        canvas.itemconfig(card_word, text="You've learned all words!", fill="black")
        canvas.itemconfig(card_background, image=card_front_img)
        # Disable buttons to prevent errors on further clicks.
        known_button.config(state="disabled")
        unknown_button.config(state="disabled")
        return # Exit the function.

    # Pick a random word from the to_learn list.
    current_card = random.choice(to_learn)

    # Configure the canvas to show the German side of the card (the front).
    canvas.itemconfig(card_title, text="German", fill="black")
    canvas.itemconfig(card_word, text=current_card["German"], fill="black")
    canvas.itemconfig(card_background, image=card_front_img)

    # Set a new timer to flip the card to the English side after 3 seconds (3000 ms).
    flip_timer = window.after(3000, flip_card)


def flip_card():
    """Flips the card to reveal the English translation."""
    # Configure the canvas to show the English side of the card (the back).
    canvas.itemconfig(card_title, text="English", fill="white")
    canvas.itemconfig(card_word, text=current_card["English"], fill="white")
    canvas.itemconfig(card_background, image=card_back_img)


def is_known():
    """
    Triggered by the 'known' (check) button.
    Removes the current word from the 'to_learn' list and saves the progress.
    """
    global to_learn
    
    # Only try to remove the card if it's still in the list to prevent errors.
    if current_card in to_learn:
        to_learn.remove(current_card)

    # Create a new DataFrame from the updated 'to_learn' list and save it to the progress file.
    # This ensures that the learned word will not appear in the next session.
    # This now correctly saves an empty file when the last word is learned.
    pd.DataFrame(to_learn).to_csv(PROGRESS_FILE, index=False)
    
    # Display the next card.
    next_card()


def reset_progress():
    """
    Resets all progress by overwriting the learning file with the original full word list.
    """
    global to_learn
    # Load the original, complete dataset.
    original_data = pd.read_csv(DATA_FILE)
    # Convert it to a list of dictionaries and update the global 'to_learn' variable.
    to_learn = original_data.to_dict(orient="records")
    # Overwrite the progress file with the full dataset.
    pd.DataFrame(to_learn).to_csv(PROGRESS_FILE, index=False)
    
    # Re-enable buttons if they were disabled from a previous completion.
    known_button.config(state="normal")
    unknown_button.config(state="normal")

    # Show a new card to restart the learning process.
    next_card()


# --------------------------- UI SETUP --------------------------- #
# Initialize the main application window.
window = Tk()
window.title("Flashy - Learn German")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

# Initialize the flip timer. It will be managed by the next_card() function.
# The initial call here is just to create the variable.
flip_timer = window.after(3000, flip_card)

# --- Canvas for Flashcard ---
# The canvas widget will hold the card image and the text.
canvas = Canvas(width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)
card_front_img = PhotoImage(file="images/card_front.png")
card_back_img = PhotoImage(file="images/card_back.png")

# Create the card background image on the canvas. It will be updated to show front or back.
card_background = canvas.create_image(400, 263, image=card_front_img)
# Create text elements for the language title and the word itself.
card_title = canvas.create_text(400, 150, text="", font=("Ariel", 40, "italic"))
card_word = canvas.create_text(400, 263, text="", font=("Ariel", 60, "bold"))
canvas.grid(row=0, column=0, columnspan=2)

# --- Buttons ---
# 'Unknown' button (cross mark) - simply moves to the next card without removing the current one.
cross_image = PhotoImage(file="images/wrong.png")
unknown_button = Button(image=cross_image, highlightthickness=0, command=next_card)
unknown_button.grid(row=1, column=0)

# 'Known' button (check mark) - calls the is_known function to remove the word and save progress.
check_image = PhotoImage(file="images/right.png")
known_button = Button(image=check_image, highlightthickness=0, command=is_known)
known_button.grid(row=1, column=1)

# 'Reset Progress' button
reset_button = Button(text="Reset Progress", command=reset_progress, font=("Ariel", 12, "bold"), bg="white")
reset_button.grid(row=2, column=0, columnspan=2, pady=20) # Added more padding for better spacing

# --------------------------- START PROGRAM --------------------------- #
# Call next_card() for the first time to load the first word and start the app.
next_card()

# Start the Tkinter event loop. This keeps the window open and responsive to user input.
window.mainloop()