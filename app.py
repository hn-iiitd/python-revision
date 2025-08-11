# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import os

# The static_folder points to your 'frontend' directory.
app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.get_json()
    code = data.get('code', '')

    if not code:
        return jsonify({'stdout': '', 'stderr': 'No code provided.'}), 400

    try:
        result = subprocess.run(
            ['python', '-c', code],
            capture_output=True,
            text=True,
            timeout=5
        )
        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({
            'stdout': '',
            'stderr': 'Execution timed out after 5 seconds.'
        }), 408
    except Exception as e:
        return jsonify({
            'stdout': '',
            'stderr': f'An unexpected error occurred: {str(e)}'
        }), 500

# This is a "catch-all" route.
# If a request doesn't match /execute, it serves the index.html file.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(port=5001, debug=True)
