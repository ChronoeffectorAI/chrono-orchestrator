from flask import Flask, request, jsonify
from orchestrator import Orchestrator
import traceback
from typing import Dict, Any

app = Flask(__name__)
orchestrator = Orchestrator()

@app.route('/api/query', methods=['POST'])
def query() -> tuple[Dict[str, Any], int]:
    try:
        data = request.json
        print(data)
        if not data or 'input' not in data:
            return jsonify({"error": "No input provided", "status": "error"}), 400
        
        user_input = data['input']
        if not isinstance(user_input, str):
            return jsonify({"error": "Input must be a string", "status": "error"}), 400
        
        response = orchestrator.handle_input(user_input)
        return jsonify(response), 200
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "status": "error",
            "type": "server"
        }), 500

@app.route('/health', methods=['GET'])
def health_check() -> tuple[Dict[str, str], int]:
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True) 