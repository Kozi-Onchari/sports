# main.py
# This is the main file for our sports prediction API.
# It uses the Flask web framework to create an API endpoint that can be used to predict match outcomes.

from flask import Flask, request, jsonify
import random

# Initialize the Flask application
app = Flask(__name__)

# --- Dummy Prediction Model ---
# In a real-world application, you would replace this with a sophisticated machine learning model.
# This model would be trained on historical match data.
# For this example, we'll use a simple function that returns a random prediction.

def predict_match_outcome(sport, team_a, team_b, team_a_form, team_b_form):
    """
    Predicts the outcome of a match based on the sport and team data.

    Args:
        sport (str): The sport being played (e.g., 'football', 'basketball', 'rugby').
        team_a (str): The name of the home team.
        team_b (str): The name of the away team.
        team_a_form (list): A list of recent results for team A ('W' for win, 'D' for draw, 'L' for loss).
        team_b_form (list): A list of recent results for team B.

    Returns:
        dict: A dictionary containing the predicted outcome.
    """
    # Simple logic: Give a slight advantage to the team with more recent wins.
    team_a_wins = team_a_form.count('W')
    team_b_wins = team_b_form.count('W')

    # A very basic weighting system
    if team_a_wins > team_b_wins:
        winner = team_a
        loser = team_b
        confidence = 0.5 + (team_a_wins - team_b_wins) * 0.05
    elif team_b_wins > team_a_wins:
        winner = team_b
        loser = team_a
        confidence = 0.5 + (team_b_wins - team_a_wins) * 0.05
    else:
        # If form is equal, pick a random winner. In 'football', a draw is also possible.
        if sport == 'football':
            outcome = random.choice([team_a, team_b, 'Draw'])
            if outcome == 'Draw':
                return {
                    'prediction': 'Draw',
                    'confidence': random.uniform(0.3, 0.5)
                }
            winner = outcome
            loser = team_b if winner == team_a else team_a
        else: # Basketball and Rugby don't typically have draws
            winner = random.choice([team_a, team_b])
            loser = team_b if winner == team_a else team_a
        confidence = 0.5

    # Ensure confidence is capped at a reasonable level
    confidence = min(confidence, 0.95)

    return {
        'prediction': 'win',
        'winning_team': winner,
        'losing_team': loser,
        'confidence': round(confidence, 2)
    }

# --- API Endpoint ---
# This defines the '/predict' endpoint, which will receive POST requests with match data.

@app.route('/predict', methods=['POST'])
def predict():
    """
    Handles the prediction requests.
    It expects a JSON payload with the sport and details of the two teams.
    """
    # Get the JSON data from the request
    data = request.get_json()

    # --- Input Validation ---
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required_fields = ['sport', 'team_a', 'team_b', 'team_a_form', 'team_b_form']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    sport = data.get('sport').lower()
    team_a = data.get('team_a')
    team_b = data.get('team_b')
    team_a_form = data.get('team_a_form')
    team_b_form = data.get('team_b_form')

    # --- Sport Validation ---
    supported_sports = ['football', 'basketball', 'rugby']
    if sport not in supported_sports:
        return jsonify({'error': f"Sport '{sport}' is not supported. Supported sports are: {supported_sports}"}), 400

    # --- Get Prediction ---
    try:
        prediction_result = predict_match_outcome(sport, team_a, team_b, team_a_form, team_b_form)
        return jsonify(prediction_result)
    except Exception as e:
        # Generic error handler for unexpected issues in the prediction logic
        return jsonify({'error': 'An error occurred during prediction.', 'details': str(e)}), 500

# --- Home Route ---
# A simple route to confirm the API is running.

@app.route('/', methods=['GET'])
def index():
    """
    A simple endpoint to show that the API is running.
    """
    return "<h1>Sports Prediction API</h1><p>Send a POST request to /predict to get a match outcome.</p>"

# --- Running the App ---
# This part of the script runs the Flask development server.
# In a production environment, you would use a more robust server like Gunicorn.

if __name__ == '__main__':
    # Runs the app on localhost, port 5000
    # The host '0.0.0.0' makes it accessible from other devices on the same network.
    app.run(host='0.0.0.0', port=5000, debug=True)

