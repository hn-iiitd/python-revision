# app.py
# This Flask application provides a single API endpoint to execute Python code securely.

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

# Initialize the Flask app.
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow requests from your frontend.
CORS(app)

@app.route('/execute', methods=['POST'])
def execute_code():
    """
    Executes Python code received from a POST request in a secure subprocess.
    Returns the standard output and standard error as a JSON response.
    """
    # Get the JSON data from the request.
    data = request.get_json()
    # Extract the 'code' field, defaulting to an empty string if not found.
    code = data.get('code', '')

    if not code:
        return jsonify({'stdout': '', 'stderr': 'No code provided.'}), 400

    try:
        # Run the code in a separate, isolated Python process.
        # This is a critical security measure to prevent the user's code
        # from affecting the server environment.
        result = subprocess.run(
            ['python', '-c', code],
            capture_output=True,  # Capture stdout and stderr.
            text=True,            # Decode stdout/stderr as text.
            timeout=5             # Set a 5-second timeout to prevent long-running code.
        )
        # Return the captured output in a JSON object.
        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr
        })
    except subprocess.TimeoutExpired:
        # Handle cases where the code takes too long to execute.
        return jsonify({
            'stdout': '',
            'stderr': 'Execution timed out after 5 seconds.'
        }), 408 # Request Timeout
    except Exception as e:
        # Handle other potential errors during subprocess execution.
        return jsonify({
            'stdout': '',
            'stderr': f'An unexpected error occurred: {str(e)}'
        }), 500 # Internal Server Error

if __name__ == '__main__':
    # This block is for local development only.
    # Render will use Gunicorn to run the app in production.
    app.run(port=5001, debug=True)
