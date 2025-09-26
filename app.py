from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Med42 AI API configuration
MED42_API_URL = os.getenv('MED42_API_URL', 'https://api.med42.ai/v1')
MED42_API_KEY = os.getenv('MED42_API_KEY')

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'NeoCura Med42 Integration',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/webhook', methods=['POST'])
def med42_webhook():
    """Handle incoming webhooks from Med42 AI"""
    try:
        # Get the webhook payload
        payload = request.get_json()
        
        if not payload:
            return jsonify({'error': 'No JSON payload received'}), 400
        
        # Log the incoming webhook
        print(f"Received webhook: {payload}")
        
        # Process the webhook based on event type
        event_type = payload.get('event_type')
        
        if event_type == 'analysis_complete':
            return handle_analysis_complete(payload)
        elif event_type == 'error':
            return handle_error(payload)
        else:
            return jsonify({'error': f'Unknown event type: {event_type}'}), 400
            
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/analyze', methods=['POST'])
def trigger_analysis():
    """Trigger Med42 AI analysis"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text field is required'}), 400
        
        # Prepare the request to Med42 API
        headers = {
            'Authorization': f'Bearer {MED42_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        med42_payload = {
            'text': data['text'],
            'webhook_url': request.host_url + 'webhook',
            'metadata': data.get('metadata', {})
        }
        
        # Make request to Med42 API
        response = requests.post(
            f"{MED42_API_URL}/analyze",
            json=med42_payload,
            headers=headers
        )
        
        if response.status_code == 200:
            return jsonify({
                'status': 'success',
                'message': 'Analysis triggered successfully',
                'job_id': response.json().get('job_id')
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to trigger analysis',
                'details': response.text
            }), response.status_code
            
    except Exception as e:
        print(f"Error triggering analysis: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def handle_analysis_complete(payload):
    """Handle analysis completion webhook"""
    job_id = payload.get('job_id')
    results = payload.get('results', {})
    
    print(f"Analysis complete for job {job_id}: {results}")
    
    # Here you would typically:
    # 1. Store the results in your database
    # 2. Notify the user
    # 3. Trigger any downstream processes
    
    return jsonify({
        'status': 'success',
        'message': 'Analysis results processed successfully'
    })

def handle_error(payload):
    """Handle error webhook"""
    job_id = payload.get('job_id')
    error_message = payload.get('error', 'Unknown error')
    
    print(f"Error for job {job_id}: {error_message}")
    
    # Handle the error appropriately
    # Log, notify user, etc.
    
    return jsonify({
        'status': 'success',
        'message': 'Error handled successfully'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
