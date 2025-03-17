from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import shutil

# Import your existing scripts here
import Influx_LX70
import Influx_LXS
import Influx_NDuro
import Influx_NDuro_NoGPS

app = Flask(__name__)
CORS(app)  # Enable CORS so React frontend can communicate

# Endpoint to run the selected analysis
@app.route('/run-analysis', methods=['POST'])
def run_analysis():
    try:
        data = request.json

        # Extract data from request
        folder_path = data.get('folderPath')
        destination_folder = data.get('destinationFolder')
        script_name = data.get('scriptName')
        copy_folder_option = data.get('copyFolder')

        # Validate required fields
        if not folder_path or not script_name:
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: folderPath or scriptName.'
            }), 400

        # Handle copy folder logic if user selected it
        if copy_folder_option and destination_folder:
            try:
                destination_folder_path = os.path.join(destination_folder, os.path.basename(folder_path))
                shutil.copytree(folder_path, destination_folder_path)
                new_path = destination_folder_path
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': f'Error copying folder: {str(e)}'
                }), 500
        else:
            new_path = folder_path

        # Map script names to functions
        script_functions = {
            "Influx_LX70": Influx_LX70.Influx_LX70_input,
            "Influx_LXS": Influx_LXS.Influx_LXS_input,
            "Influx_NDuro": Influx_NDuro.Influx_NDuro_input,
            "Influx_NDuro_NoGPS": Influx_NDuro_NoGPS.Influx_NDuro_NoGPS_input
        }

        # Check if selected script exists
        if script_name not in script_functions:
            return jsonify({
                'status': 'error',
                'message': 'Invalid script name.'
            }), 400

        # Run the selected analysis function
        try:
            script_functions[script_name](new_path)
            return jsonify({
                'status': 'success',
                'message': f'{script_name} analysis completed successfully!'
            })
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Error running analysis: {str(e)}'
            }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500


if __name__ == '__main__':
    # You can set host='0.0.0.0' to allow external access if needed
    app.run(debug=True, port=5000)
