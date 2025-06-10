from flask import Flask, render_template, request, jsonify, send_from_directory
import json
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from main import EmailProcessingAgent

app = Flask(__name__)

@app.route('/')
def index():
    """Main page showing processing results"""
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_emails():
    """API endpoint to trigger email processing"""
    try:
        email_folder = "../emails"
        output_folder = "../output"
        
        agent = EmailProcessingAgent(email_folder, output_folder)
        results = agent.process_all_emails()
        
        return jsonify({
            'status': 'success',
            'processed_count': len(results),
            'results': results
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/results')
def get_results():
    """Get processing results"""
    try:
        results_path = "../output/processing_results.json"
        if os.path.exists(results_path):
            with open(results_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
            return jsonify(results)
        else:
            return jsonify([])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summary/<filename>')
def get_summary(filename):
    """Get detailed summary for a specific email"""
    try:
        summary_path = f"../output/{filename}"
        if os.path.exists(summary_path):
            with open(summary_path, 'r', encoding='utf-8') as f:
                summary = json.load(f)
            return jsonify(summary)
        else:
            return jsonify({'error': 'Summary not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
