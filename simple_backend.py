from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "✅ Backend Working!"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    user_type = data.get('user_type', 'client')
    
    response = f"Hello! You said: '{message}' as {user_type}. I'm your legal assistant."
    
    return jsonify({
        "response": response,
        "status": "success"
    })

@app.route('/get_lawyers', methods=['GET'])
def get_lawyers():
    return jsonify({
        "lawyers": [
            {"name": "Ali Khan", "specialization": "Family Law", "rating": 4.5},
            {"name": "Sara Ahmed", "specialization": "Criminal Law", "rating": 4.8}
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
