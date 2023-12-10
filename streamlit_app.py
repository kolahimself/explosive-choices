"""
streamlit_app.py

A Streamlit app for analyzing success and failure rates,
payouts and expected value in a mines casino game scenario.

Author:
James Kola
"""

# Required imports
import pandas as pd

from outcome_evaluation import *
import streamlit as st
import plotly.express as px

# ==================================================================#
#                          Streamlit Code                           #
# ==================================================================#

description = 'An interactive tool for analyzing success and failure rates, determining multipliers and expected value in a Mines casino game.'

st.title('Explosive Choices🎲: Mines Casino Game Analysis')
st.write(description)

# Number of squares, bet amount
with st.container():
    st.subheader('Game Options')

    # Number of squares
    amount_of_squares = st.number_input('Number of Squares on the Board', value=25)

    # Bet amount
    bet_amount = st.number_input('Enter your bet amount (in your unit currency):', value=1)

    # Mines on board
    num_mines = st.slider("Select the number of mines on the board:", min_value=2, max_value=24, step=1)

    # Spaces to be cleared
    spaces_cleared = st.number_input('Enter the desired number of spaces to be cleared:',
                                     min_value=0,
                                     max_value=25,
                                     step=1)

    def calculate_and_visualize(numbr_mines, spaces_uncovered, bet__amount, no_of_squares):
        """
        Function to calculate insights and visualize
        :param numbr_mines: Number of mines on the board
        :param spaces_uncovered: Desired no of spaces to be cleared
        :param bet__amount: Bet amount
        :param no_of_squares: Total number of squares, 25 by default
        """
        scenario = OutcomeAnalyzer(num_bombs=numbr_mines, uncovered_spaces=spaces_uncovered,
                                   bet_amount=bet__amount, amount_of_squares=no_of_squares)
        insights = scenario.insights

        # Display success and failure rates
        st.subheader('Success and Failure Rates')
        st.write(
            f'The probability of successfully clearing {spaces_cleared} spaces with {num_mines} mines is {np.round(insights["Success Rate"], 3)}%. '
            f'The chance of failure is {np.round(insights["Failure Rate"], 3)}%. Visualize the rates below:')

        # Pie chart visualization
        labels = [f'Success Rate ({np.round(insights["Success Rate"], 3)}%)',
                  f'Failure Rate ({np.round(insights["Failure Rate"], 3)}%)']
        sizes = [np.round(insights["Success Rate"], 3), np.round(insights["Failure Rate"], 3)]

        fig1 = px.pie(names=labels, values=sizes, color=labels,
                      color_discrete_map={
                          f'Success Rate ({np.round(insights["Success Rate"], 3)}%)': '#2CA02C',
                          f'Failure Rate ({np.round(insights["Failure Rate"], 3)}%)': '#D62728'
                      })

        fig1.update_layout(
            legend=dict(
                font=dict(color='red'),
                bgcolor="rgba(255, 255, 255, 0.8)"
            )
        )

        st.plotly_chart(fig1, theme="streamlit", use_container_width=True)

        # Display expected payout
        st.subheader('Expected Payout')
        st.write(f'This scenario has an expected multiplier of {insights["Multiplier"]}x')

        # Display expected value
        st.subheader('Expected Value')
        st.write(f'In this scenario, the expected value is {np.round(insights["Expected Value"] * 100, 4)}%')

        # Disclaimer
        st.subheader('Disclaimer⚠')
        st.write('This tool is intended for recreational and educational purposes only. The calculations and predictions provided are based on simulated\n'
                 'scenarios and should not be considered financial or gaming advice. Users are encouraged to use their discretion when making decisions related to real-world scenarios.')

    # Analyze the scenario
    calculate_and_visualize(num_mines, spaces_cleared, bet_amount, amount_of_squares)
