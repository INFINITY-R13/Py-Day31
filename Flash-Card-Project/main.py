from tkinter import *
import pandas as pd
import random

# --------------------------- CONSTANTS --------------------------- #
BACKGROUND_COLOR = "#B1DDC6"
DATA_FILE = "data/german_words.csv"
PROGRESS_FILE = "data/words_to_learn.csv"

# --------------------------- LOAD DATA --------------------------- #
try:
    data = pd.read_csv(PROGRESS_FILE)
    if data.empty:
        raise FileNotFoundError
except (FileNotFoundError, pd.errors.EmptyDataError):
    data = pd.read_csv(DATA_FILE)
    data.to_csv(PROGRESS_FILE, index=False)  # Ensure a progress file exists

to_learn = data.to_dict(orient="records")
current_card = {}


# --------------------------- FUNCTIONS --------------------------- #
def next_card():
    """Displays a new German word and schedules a flip after 3 seconds."""
    global current_card, flip_timer
    if not to_learn:
        canvas.itemconfig(card_title, text="Well Done!", fill="black")
        canvas.itemconfig(card_word, text="You've learned all words!", fill="black")
        return

    window.after_cancel(flip_timer)
    current_card = random.choice(to_learn)

    canvas.itemconfig(card_title, text="German", fill="black")
    canvas.itemconfig(card_word, text=current_card["German"], fill="black")
    canvas.itemconfig(card_background, image=card_front_img)

    flip_timer = window.after(3000, flip_card)


def flip_card():
    """Flips the card to show the English translation."""
    canvas.itemconfig(card_title, text="English", fill="white")
    canvas.itemconfig(card_word, text=current_card["English"], fill="white")
    canvas.itemconfig(card_background, image=card_back_img)


def is_known():
    """Removes the known word, updates the CSV, and moves to the next card."""
    global to_learn
    if current_card in to_learn:
        to_learn.remove(current_card)

    if to_learn:
        pd.DataFrame(to_learn).to_csv(PROGRESS_FILE, index=False)

    next_card()


def reset_progress():
    """Resets the progress by restoring the original dataset."""
    global to_learn
    original_data = pd.read_csv(DATA_FILE).to_dict(orient="records")
    to_learn = original_data
    pd.DataFrame(to_learn).to_csv(PROGRESS_FILE, index=False)
    next_card()


# --------------------------- UI SETUP --------------------------- #
window = Tk()
window.title("Flashy - Learn German")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

flip_timer = window.after(3000, flip_card)

canvas = Canvas(width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)
card_front_img = PhotoImage(file="images/card_front.png")
card_back_img = PhotoImage(file="images/card_back.png")

card_background = canvas.create_image(400, 263, image=card_front_img)
card_title = canvas.create_text(400, 150, text="", font=("Ariel", 40, "italic"))
card_word = canvas.create_text(400, 263, text="", font=("Ariel", 60, "bold"))
canvas.grid(row=0, column=0, columnspan=2)

# Buttons
cross_image = PhotoImage(file="images/wrong.png")
unknown_button = Button(image=cross_image, highlightthickness=0, command=next_card)
unknown_button.grid(row=1, column=0)

check_image = PhotoImage(file="images/right.png")
known_button = Button(image=check_image, highlightthickness=0, command=is_known)
known_button.grid(row=1, column=1)

# Reset Button
reset_button = Button(text="Reset Progress", command=reset_progress, font=("Ariel", 12, "bold"), bg="white")
reset_button.grid(row=2, column=0, columnspan=2, pady=10)

# Start the program
next_card()

window.mainloop()
