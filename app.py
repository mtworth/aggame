import streamlit as st
import pandas as pd
import plotly.express as px
import random
import urllib.parse

# Streamlit app title
st.html(
    """
    <div style="text-align: center;">
        <h1><span style="">🌾🍎 Croppler </span>🐮🌱</h1>
        <body>The game about US agriculture.</body>
    </div>
    """
)


# Load the dataset
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

url = "https://raw.githubusercontent.com/mtworth/agle/refs/heads/main/state_trade_estimates.csv"
data = load_data(url)

# Function to select and cache a random state for the game (so it's the same for all users)
@st.cache_resource
def select_random_state():
    return random.choice(data['State'].unique())

# Get the cached random state
random_state = select_random_state()

# Filter the data for the randomly selected state and the year 2022
filtered_data = data[(data['State'] == random_state) & (data['Year'] == 2022)]

# Remove rows with zero or NaN values in the 'Value' column
filtered_data = filtered_data[filtered_data['Value'].notna() & (filtered_data['Value'] > 0)]

# Filter out specific commodities
exclude_commodities = ["Total agricultural exports", "Total plant products", "Total animal products"]
filtered_data = filtered_data[~filtered_data['Commodity'].isin(exclude_commodities)]

# Calculate total agricultural production by state for 2022
@st.cache_data
def calculate_state_rankings(data, year):
    # Filter data for the specific year and exclude total categories
    year_data = data[
        (data['Year'] == year) & 
        (~data['Commodity'].isin(["Total agricultural exports", "Total plant products", "Total animal products"]))
    ]
    
    # Sum the values by state
    state_totals = year_data.groupby('State')['Value'].sum().reset_index()
    
    # Sort states by total value in descending order
    state_totals_sorted = state_totals.sort_values('Value', ascending=False)
    
    # Add ranking column
    state_totals_sorted['Rank'] = range(1, len(state_totals_sorted) + 1)
    
    return state_totals_sorted

# Calculate state rankings
state_rankings = calculate_state_rankings(data, 2022)

# Find the rank of the random state
state_rank = state_rankings[state_rankings['State'] == random_state]['Rank'].values[0]

# Summarize export total values by commodity
commodity_data = filtered_data.groupby('Commodity', as_index=False)['Value'].sum()

# Function to format the Value into millions (M) or billions (B)
def format_value(value):
    if value >= 1e9:
        return f"${value:.2f}B"  # Format in billions
    else:
        return f"${value:.2f}M"  # Format in millions

# Apply the formatting function to the 'Value' column
commodity_data['Formatted_Value'] = commodity_data['Value'].apply(format_value)

# Function to generate an SMS link with the game results
def generate_sms_link(guesses, state, success):
    performance = "".join(guesses)
    status = "Success! 🎉" if success else "Game Over. ❌"
    message = f"Guess ag production! My performance today {performance}. https://croppler.streamlit.app/"
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
    st.write(f"Attempts used: {attempts}/5")
    
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

    # Display the state rank clue
    st.info(f"**Instructions:** Guess which state exported these agriculture products!   \n   \n **Clue** 🌟: This state ranks {state_rank} in total agricultural production in 2022.")

    # Create a treemap using Plotly
    if not commodity_data.empty:
        fig = px.treemap(
            commodity_data,
            path=['Commodity'],  # Treemap partition by commodity
            values='Value',  # Size of partitions based on export total value
            title=f"",
            color='Value',  # Color intensity based on export value
            color_continuous_scale='Viridis',
            hover_data={'Commodity': True, 'Formatted_Value': True}  # Show formatted value on hover
        )
        
        # Add text labels for total value (formatted in millions or billions)
        fig.update_traces(
            textinfo="label+value",  # Display the label (commodity) and value
            customdata=commodity_data['Formatted_Value'],  # Pass formatted values as custom data
            texttemplate="%{label}<br>%{customdata}",  # Show formatted value as custom data
        )
        
        # Remove black background by updating layout
        fig.update_layout(
            paper_bgcolor='white',  # Set background to white
            plot_bgcolor='white',   # Set plot background to white
            showlegend=False        # Remove the legend
        )
        
        # Display the treemap
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"No valid data available for {random_state} in 2022.")
    
    st.write("You have five attempts to guess the hidden state name.")

    # Dropdown for user to guess the state
    guess = st.selectbox("Select your guess:", data['State'].unique(), key="guess_select")

    if st.button("Submit Guess"):
        if st.session_state.guessed_correctly:
            st.warning("You already completed the game! 🎉")
        elif guess:
            st.session_state.attempts += 1
            if guess.lower() == random_state.lower():
                st.session_state.guessed_correctly = True
                st.session_state.guesses.append("🟢")
            else:
                st.session_state.guesses.append("🟡")

            # Check if the game should end
            if st.session_state.attempts == 5 or st.session_state.guessed_correctly:
                game_result_dialog(
                    random_state,
                    st.session_state.attempts,
                    st.session_state.guesses,
                    st.session_state.guessed_correctly,
                )

    # Display guesses so far
    st.write("Your guesses so far:")
    st.write(" ".join(st.session_state.guesses) or "No guesses yet!")

    # Display remaining attempts
    st.write(f"Attempts: {st.session_state.attempts}/5")

if __name__ == "__main__":
    main()
