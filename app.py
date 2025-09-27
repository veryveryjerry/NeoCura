from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Med42 AI API configuration
MED42_API_URL = os.getenv('MED42_API_URL', 'https://api.med42.ai/v1')
MED42_API_KEY = os.getenv('MED42_API_KEY')

# Fallback response message
FALLBACK_MESSAGE = 'Sorry, I couldn\'t get a medical response at this time. Please try again later or consult with a healthcare professional.'

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
    """Handle incoming webhooks from Med42 AI with improved error handling"""
    try:
        # Get the webhook payload
        payload = request.get_json()
        
        if not payload:
            print("Warning: No JSON payload received")
            return jsonify({
                'error': 'No JSON payload received',
                'fallback_message': FALLBACK_MESSAGE
            }), 400
        
        # Log the incoming webhook
        print(f"Received webhook: {payload}")
        
        # Process the webhook based on event type
        event_type = payload.get('event_type')
        
        if event_type == 'analysis_complete':
            return handle_analysis_complete(payload)
        elif event_type == 'error':
            return handle_error(payload)
        elif not event_type:
            print("Warning: Missing event_type in webhook payload")
            return jsonify({
                'error': 'Missing event_type in payload',
                'fallback_message': FALLBACK_MESSAGE,
                'status': 'handled'
            }), 200  # Return 200 to acknowledge receipt
    
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({
            'error': 'Internal webhook processing error',
            'fallback_message': FALLBACK_MESSAGE
        }), 200  # Return 200 to acknowledge receipt
    
    return jsonify({
        'status': 'handled',
        'message': 'Unknown event type processed'
    }), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    """Hybrid analyze endpoint - supports both direct chat Q&A and Med42 job processing"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Text field is required',
                'fallback_message': FALLBACK_MESSAGE
            }), 400
        
        # Check if this is a direct chat request (has 'direct_response' flag or no webhook_url)
        is_direct_chat = data.get('direct_response', False) or not data.get('webhook_url')
        
        if is_direct_chat:
            # Handle as direct chat Q&A
            return handle_direct_chat(data)
        else:
            # Handle as Med42 job (original behavior)
            return trigger_med42_analysis(data)
            
    except Exception as e:
        print(f"Error in analyze endpoint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'fallback_message': FALLBACK_MESSAGE
        }), 200

def handle_direct_chat(data):
    """Handle direct chat Q&A requests"""
    try:
        # Prepare request for direct chat to Med42
        headers = {
            'Authorization': f'Bearer {MED42_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Use synchronous chat endpoint instead of async analysis
        chat_payload = {
            'text': data['text'],
            'metadata': data.get('metadata', {})
        }
        
        # Make direct request to Med42 chat/completion endpoint
        response = requests.post(
            f"{MED42_API_URL}/chat",  # Different endpoint for direct responses
            json=chat_payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Extract the response text
            ai_response = response_data.get('response', response_data.get('text', ''))
            
            if not ai_response:
                return jsonify({
                    'status': 'warning',
                    'message': 'No response from AI',
                    'fallback_message': FALLBACK_MESSAGE
                }), 200
            
            return jsonify({
                'status': 'success',
                'response': ai_response,
                'type': 'direct_chat'
            })
        else:
            print(f"Chat API error: {response.status_code} - {response.text}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to get AI response',
                'fallback_message': FALLBACK_MESSAGE
            }), 200
            
    except requests.exceptions.Timeout:
        return jsonify({
            'status': 'error',
            'message': 'AI response timeout',
            'fallback_message': FALLBACK_MESSAGE
        }), 200
    except requests.exceptions.ConnectionError:
        return jsonify({
            'status': 'error',
            'message': 'Unable to connect to AI service',
            'fallback_message': FALLBACK_MESSAGE
        }), 200
    except Exception as e:
        print(f"Direct chat error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Chat processing error',
            'fallback_message': FALLBACK_MESSAGE
        }), 200

def trigger_med42_analysis(data):
    """Trigger Med42 AI analysis job (original functionality)"""
    try:
        # Prepare the request to Med42 API
        headers = {
            'Authorization': f'Bearer {MED42_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        med42_payload = {
            'text': data['text'],
            'webhook_url': data.get('webhook_url', request.host_url + 'webhook'),
            'metadata': data.get('metadata', {})
        }
        
        # Make request to Med42 API
        response = requests.post(
            f"{MED42_API_URL}/analyze",
            json=med42_payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            job_id = response_data.get('job_id')
            
            if not job_id:
                print("Warning: API returned 200 but no job_id")
                return jsonify({
                    'status': 'warning',
                    'message': 'Analysis may have started but no job ID returned',
                    'fallback_message': FALLBACK_MESSAGE
                }), 200
                
            return jsonify({
                'status': 'success',
                'message': 'Analysis triggered successfully',
                'job_id': job_id,
                'type': 'med42_job'
            })
        else:
            print(f"API error: {response.status_code} - {response.text}")
            return jsonify({
                'status': 'error',
                'message': 'Failed to trigger analysis',
                'fallback_message': FALLBACK_MESSAGE,
                'details': response.text[:200]
            }), 200
            
    except requests.exceptions.Timeout:
        print("API request timeout")
        return jsonify({
            'status': 'error',
            'message': 'API request timeout',
            'fallback_message': FALLBACK_MESSAGE
        }), 200
    except requests.exceptions.ConnectionError:
        print("API connection error")
        return jsonify({
            'status': 'error',
            'message': 'Unable to connect to medical AI service',
            'fallback_message': FALLBACK_MESSAGE
        }), 200
    except Exception as e:
        print(f"Error triggering analysis: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error',
            'fallback_message': FALLBACK_MESSAGE
        }), 200

def handle_analysis_complete(payload):
    """Handle analysis completion webhook with improved validation"""
    job_id = payload.get('job_id')
    results = payload.get('results', {})
    
    print(f"Analysis complete for job {job_id}: {results}")
    
    # Validate results
    if not results or (isinstance(results, dict) and not results):
        print(f"Warning: Empty results for job {job_id}")
        return jsonify({
            'status': 'warning',
            'message': 'Analysis completed but no results available',
            'fallback_message': FALLBACK_MESSAGE,
            'job_id': job_id
        })
    
    # Check for meaningful content in results
    if isinstance(results, dict):
        text_content = results.get('text', '').strip()
        if not text_content:
            print(f"Warning: No text content in results for job {job_id}")
            return jsonify({
                'status': 'warning',
                'message': 'Analysis completed but no meaningful response',
                'fallback_message': FALLBACK_MESSAGE,
                'job_id': job_id
            })
    
    # Here you would typically:
    # 1. Store the results in your database
    # 2. Notify the user
    # 3. Trigger any downstream processes
    
    return jsonify({
        'status': 'success',
        'message': 'Analysis results processed successfully',
        'job_id': job_id,
        'has_results': True
    })

def handle_error(payload):
    """Handle error webhook with improved user messaging"""
    job_id = payload.get('job_id')
    error_message = payload.get('error', 'Unknown error')
    
    print(f"Error for job {job_id}: {error_message}")
    
    # Handle the error appropriately
    # Log, notify user, etc.
    
    return jsonify({
        'status': 'error',
        'message': 'Analysis failed',
        'fallback_message': FALLBACK_MESSAGE,
        'job_id': job_id,
        'error_details': error_message[:100]  # Limit error details
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
