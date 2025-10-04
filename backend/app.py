from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

# Path to the meteors data file
data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'meteors.json')

@app.route('/api/meteors', methods=['GET'])
def get_meteors():
    try:
        with open(data_path, 'r') as file:
            meteors_data = json.load(file)
        return jsonify(meteors_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Meteor-X backend server...")
    app.run(debug=True, port=5000)
