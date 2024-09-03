import os
from flask import Flask, jsonify, request
from flask_compress import Compress
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
Compress(app)  # Enable compression for all responses

# Initialize Firebase Admin SDK
cred = credentials.Certificate(os.getenv('FIREBASE_ADMIN_CREDENTIALS'))
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

# Root route
@app.route('/')
def index():
    return jsonify({'message': 'Welcome to the Smart Irrigation API!'})

# 1. Get Farmer Details
@app.route('/api/farmers/<farmer_id>', methods=['GET'])
def get_farmer_details(farmer_id):
    try:
        farmer_ref = db.collection('farmers').document(farmer_id)
        farmer_doc = farmer_ref.get()
        if farmer_doc.exists:
            farmer_data = farmer_doc.to_dict()
            return jsonify({'status': 'success', 'data': farmer_data}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Farmer not found.'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 2. Get Farmer's Crop Details
@app.route('/api/farmers/<farmer_id>/crops/<crop_id>', methods=['GET'])
def get_specific_crop(farmer_id, crop_id):
    try:
        crop_ref = db.collection('farmers').document(farmer_id).collection('crops').document(crop_id)
        crop_doc = crop_ref.get()
        if crop_doc.exists:
            crop_data = crop_doc.to_dict()
            return jsonify({'status': 'success', 'data': crop_data}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Crop not found.'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 3. Update Farmer's Crop Details
@app.route('/api/farmers/<farmer_id>/crops/<crop_id>', methods=['PUT'])
def update_farmer_crop(farmer_id, crop_id):
    try:
        data = request.get_json()
        crop_ref = db.collection('farmers').document(farmer_id).collection('crops').document(crop_id)
        crop_ref.update(data)
        return jsonify({'status': 'success', 'message': 'Crop details updated successfully.'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 4. Add a New Crop for a Farmer
@app.route('/api/farmers/<farmer_id>/crops', methods=['POST'])
def add_farmer_crop(farmer_id):
    try:
        data = request.get_json()
        crops_ref = db.collection('farmers').document(farmer_id).collection('crops')
        new_crop_ref = crops_ref.add(data)
        return jsonify({'status': 'success', 'message': 'Crop added successfully.', 'crop_id': new_crop_ref[1].id}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# 5. Delete a Crop for a Farmer
@app.route('/api/farmers/<farmer_id>/crops/<crop_id>', methods=['DELETE'])
def delete_farmer_crop(farmer_id, crop_id):
    try:
        crop_ref = db.collection('farmers').document(farmer_id).collection('crops').document(crop_id)
        crop_ref.delete()
        return jsonify({'status': 'success', 'message': 'Crop deleted successfully.'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
