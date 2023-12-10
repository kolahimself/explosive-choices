"""
outcome_evaluation.py

Script for analyzing success and failure rates, payouts and expected values in a mines game scenario.

Requires:
- Number of bombs set on the board
- Spaces cleared

Author:
James Kola
"""

# Import necessary libraries
import numpy as np
import pandas as pd
import cryptpandas as crp
from scipy import interpolate
from functools import reduce


class OutcomeAnalyzer:
    """
    A class for analyzing success and failure rates, payouts and expected value in a mines game scenario.

    Attributes:
        - num_bombs (int): Number of bombs in the scenario.
        - uncovered_spaces (int): The number of spaces cleared in the scenario.
        - amount_of_squares (int): Amount of squares on the board, 25 by default.
        - bet_amount (float): Amount used as bet, 1 unit ($ or any other currency) by default.

        Results (dict):
        - Success Rate (float): Percentage of successfully uncovered spaces.
        - Failure Rate (float): Percentage of unsuccessfully uncovered spaces.
        - Multiplier (float): Predicted multiplier for the scenario.
        - Expected Value (float): The expected value of a specific bet.
    """

    def __init__(self, num_bombs: int, uncovered_spaces: int, bet_amount=1, amount_of_squares=25):
        """
        Initialize the OutcomeAnalyzer with the number of bombs and covered spaces

        Attributes:
        :param num_bombs (int): Number of bombs in the scenario.
        :param uncovered_spaces (int): The number of uncovered spaces in the scenario.
        :param amount_of_squares (int): Amount of squares on the board, 25 by default.
        :param bet_amount (float): Amount used as bet, 1 unit ($ or any other currency) by default.
        """
        self.num_bombs = num_bombs
        self.uncovered_spaces = uncovered_spaces
        self.amount_of_squares = amount_of_squares
        self.bet_amount = bet_amount

        # Results
        self.insights = {
            'Success Rate': 0,
            'Failure Rate': 0,
            'Multiplier': 0.00,
            'Expected Value': 0.0
        }

        # Determine spaces covered
        self.covered_spaces = self.amount_of_squares - self.uncovered_spaces

        # Determine success and failure rates
        self.calculate_success_failure_rates()

        # Predict Payout/multiplier
        self.predict_multiplier()

        # Calculate expected value
        self.calculate_expected_value()

    def calculate_success_failure_rates(self):
        """
        Calculate success and failure rates based on the number of bombs and covered spaces.

        Updates:
            - Success Rate (float): Percentage of successfully uncovered spaces.
            - Failure Rate (float): Percentage of unsuccessfully uncovered spaces.
        """
        # Calculate success rate using functools.reduce
        success_rate = reduce(
            lambda x, i: x * ((self.amount_of_squares - self.num_bombs - i) / (self.amount_of_squares - i)),
            range(self.uncovered_spaces),
            1
        )

        # Save the values in the insight dictionary
        self.insights['Success Rate'] = success_rate * 100
        self.insights['Failure Rate'] = 100 - self.insights['Success Rate']

    def predict_multiplier(self):
        """
        Predicts the multiplier based on manually sampled data.

        Uses:
            - Number of bombs
            - Sampled data on uncovered spaces and multipliers

        Updates:
            - Multiplier (float): Predicted multiplier for the scenario.
        """

        def load_sample_data_packet(num_bombs: int):
            """
            Function that receives number of bombs as input,
            then compares with the manually calculated data to output sample uncovered spaces and the multipliers.
            :param num_bombs: Number of bombs in the scenario.
            :return: data_packets (dict) contain sample uncovered spaces and the multipliers
            """
            smcd = crp.read_encrypted('assets/dmsc.crypt', '-%nPGS;GIC,2x}2I')

            # Create a dictionary to store the manually collected data
            data_packets = {}

            # Iterate over unique int values
            for unique_int in smcd['A'].unique():
                # Create a new dataframe for the unique value
                temp_ednt = smcd[smcd['A'] == unique_int][['B', 'C']]

                # Update the data packet dict
                # num_bombs is the key, then sample uncovered spaces and multipliers are the values.
                data_packets[unique_int] = temp_ednt

            return data_packets[num_bombs]

        # Identify number of bombs to load the appropriate sample data packet
        data_packet = load_sample_data_packet(self.num_bombs)
        print(data_packet)

        # Define Predict Function with manually collected samples, uses `scipy.interpolate.interp1d`
        # B for Number of uncovered spaces, C for collected payouts
        predictor = interpolate.interp1d(x=data_packet['B'], y=data_packet['C'],
                                         fill_value='extrapolate')

        # Predict the multiplier given the covered spaces
        self.insights['Multiplier'] = float(predictor(self.covered_spaces))

    def calculate_expected_value(self):
        """
        Calculates the expected value of a specific bet.

        Uses:
            - Success Rate
            - Failure Rate
            - Multiplier
            - Bet amount

        Updates:
            - Expected Value (float): The expected value of a specific bet.
        """
        # Retrieve needed parameters
        prob_of_winning = self.insights['Success Rate'] / 100
        prob_of_losing = self.insights['Failure Rate'] / 100
        multiplier = self.insights['Multiplier']
        bet_amount = self.bet_amount

        # Determine the expected value of the bet
        expected_value = ((prob_of_winning * (multiplier - bet_amount)) + (prob_of_losing * -bet_amount)) / bet_amount

        # Store the expected value of the bet
        self.insights['Expected Value'] = expected_value
