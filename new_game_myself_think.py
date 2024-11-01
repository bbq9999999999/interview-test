import requests
import time

def get_wordle_feedback(guess, seed):
    url = 'https://wordle.votee.dev:8000/random'
    params = {'guess': guess, 'seed': seed}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Ensure we catch HTTP errors
        feedback = response.json()   # Parse the JSON response
        return feedback

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)
        return None

# Function to make guesses from a to z and analyze feedback
def guess_word_with_alphabet(seed, word_length=5):
    start_time = time.time()  # Start time tracking

    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    known_positions = [''] * word_length  # Initialize known letters at each position
    possible_letters = set(alphabet)      # Start with all letters in the alphabet

    for letter in alphabet:
        # Guess the letter repeated to match word length, e.g., "aaaaa"
        guess = letter * word_length
        feedback = get_wordle_feedback(guess, seed)

        # Exit if feedback not returned
        if feedback is None:
            return "Could not get feedback from API."

        # Analyze feedback for the guessed letter
        for item in feedback:
            slot = item['slot']
            guessed_letter = item['guess']
            result = item['result']

            if result == 'correct':
                known_positions[slot] = guessed_letter  # Confirm the letter and position
            elif result == 'present':
                possible_letters.add(guessed_letter)    # Add to possible letters if present elsewhere
            elif result == 'absent' and guessed_letter in possible_letters:
                possible_letters.remove(guessed_letter) # Remove absent letters

        # Build guess word based on known positions and possible letters
        guess = ''.join([letter if letter in known_positions else possible_letters.pop()
                         for letter in known_positions])

        # Check if guess is fully filled
        if all(known_positions):
            end_time = time.time()  # End time tracking
            duration = end_time - start_time
            print("Guessed word:", ''.join(known_positions))
            print(f"Time taken: {duration:.2f} seconds")
            return ''.join(known_positions)

    end_time = time.time()  # End time tracking if unable to determine
    duration = end_time - start_time
    print(f"Unable to determine the word within alphabet guesses. Time taken: {duration:.2f} seconds")
    return "Unable to determine the word within alphabet guesses."

# Example usage
seed = 42  # Replace with the actual seed for the game
result = guess_word_with_alphabet(seed)
print("Result:", result)