from flask import Flask, request, jsonify
from flask_cors import CORS
import chatbot_logic
import firebase_admin
from firebase_admin import credentials, firestore
import os
import time  # ✅ STEP 1: ADD THIS LINE

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

# Initialize Firebase (you'll need your Firebase credentials JSON file)
try:
    cred = credentials.Certificate("path/to/your/firebase-credentials.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase connected successfully")
except:
    print("⚠️  Firebase not connected. Using mock data.")
    db = None

@app.route('/')
def home():
    return "Zakoota Chatbot Backend is Running!"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # ✅ STEP 1: START TIMER
        start_time = time.time()
        
        data = request.json
        user_message = data.get('message', '')
        user_type = data.get('user_type', 'client')  # 'client' or 'lawyer'
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Get response from chatbot logic
        response = chatbot_logic.get_response(user_message, user_type, db)
        
        # ✅ STEP 1: END TIMER AND PRINT
        end_time = time.time()
        response_time = end_time - start_time
        print(f"🕒 RESPONSE TIME: {response_time:.3f} seconds")
        
        return jsonify({
            "response": response,
            "status": "success",
            "response_time": f"{response_time:.3f}s"  # Optional: send to frontend
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_lawyers', methods=['GET'])
def get_lawyers():
    """API to get all lawyers from database"""
    try:
        if db:
            lawyers_ref = db.collection('lawyers')
            docs = lawyers_ref.stream()
            lawyers = []
            for doc in docs:
                lawyer_data = doc.to_dict()
                lawyer_data['id'] = doc.id
                lawyers.append(lawyer_data)
            return jsonify({"lawyers": lawyers})
        else:
            # Mock data for testing
            return jsonify({
                "lawyers": [
                    {"name": "Ali Khan", "specialization": "Family Law", "rating": 4.5},
                    {"name": "Sara Ahmed", "specialization": "Criminal Law", "rating": 4.8}
                ]
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5005))
    app.run(debug=False, host='0.0.0.0', port=port)