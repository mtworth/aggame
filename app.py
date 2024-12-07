import streamlit as st
import urllib.parse

# Define the hidden state
HIDDEN_STATE = "California"  # Change this to any state name
MAX_ATTEMPTS = 5

# Function to generate an SMS link with the game results
def generate_sms_link(guesses, state, success):
    performance = "".join(guesses)
    status = "Success! 🎉" if success else "Game Over. ❌"
    message = f"{status} Hidden state: {state}. Your performance: {performance}."
    recipient = ""  # Replace with a default number if needed, or leave blank
    sms_link = f"sms:{recipient}?body={urllib.parse.quote(message)}"
    return sms_link

# Function to handle the game completion dialog
@st.dialog("Game Result")
def game_result_dialog(state, attempts, guesses, success):
    if success:
        st.success(f"🎉 Success! The hidden state was {state}.")
    else:
        st.error(f"❌ Game over! The hidden state was {state}.")
    
    st.write("Your performance:")
    st.write(" ".join(guesses))
    st.write(f"Attempts used: {attempts}/{MAX_ATTEMPTS}")
    
    # Generate the SMS link
    sms_link = generate_sms_link(guesses, state, success)
    st.markdown(f"[Click here to share your results via SMS!]({sms_link})")
    
    if st.button("Play Again"):
        # Reset the session state for a new game
        del st.session_state.attempts
        del st.session_state.guesses
        del st.session_state.guessed_correctly
        st.rerun()

# Main app logic
def main():
    # Initialize session state
    if "attempts" not in st.session_state:
        st.session_state.attempts = 0
        st.session_state.guesses = []
        st.session_state.guessed_correctly = False

    st.title("Guess the Hidden State!")
    st.write("You have five attempts to guess the hidden state name.")

    # Input box for user to guess the state
    guess = st.text_input("Enter your guess:", key="guess_input").strip()

    if st.button("Submit Guess"):
        if st.session_state.guessed_correctly:
            st.warning("You already completed the game! 🎉")
        elif guess:
            st.session_state.attempts += 1
            if guess.lower() == HIDDEN_STATE.lower():
                st.session_state.guessed_correctly = True
                st.session_state.guesses.append("🟢")
            else:
                st.session_state.guesses.append("🟡")

            # Check if the game should end
            if st.session_state.attempts == MAX_ATTEMPTS or st.session_state.guessed_correctly:
                game_result_dialog(
                    HIDDEN_STATE,
                    st.session_state.attempts,
                    st.session_state.guesses,
                    st.session_state.guessed_correctly,
                )

    # Display guesses so far
    st.write("Your guesses so far:")
    st.write(" ".join(st.session_state.guesses) or "No guesses yet!")

    # Display remaining attempts
    st.write(f"Attempts: {st.session_state.attempts}/{MAX_ATTEMPTS}")

if __name__ == "__main__":
    main()
