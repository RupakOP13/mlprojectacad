"""
SMS Spam Detector - Flask Web Application
"""

import os
import sys
import json
import joblib
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from src.preprocessing import preprocess, extract_features
from src.model import load_best_model, load_metadata

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sms-spam-detector-secret-2024'

#  Global model cache 
_model = None
_metadata = None

def get_model():
    global _model
    if _model is None:
        _model = load_best_model()
    return _model

def get_metadata():
    global _metadata
    if _metadata is None:
        _metadata = load_metadata()
    return _metadata

#  Routes 
@app.route('/')
def index():
    meta = get_metadata()
    return render_template('index.html', metadata=meta)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    message = data['message'].strip()
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    try:
        model = get_model()
        cleaned = preprocess(message)
        
        prediction = model.predict([cleaned])[0]
        proba = model.predict_proba([cleaned])[0]
        
        spam_prob = float(proba[1]) * 100
        ham_prob = float(proba[0]) * 100
        
        # Extract features for transparency
        features = extract_features(message)
        
        result = {
            'prediction': 'SPAM' if prediction == 1 else 'HAM',
            'is_spam': bool(prediction == 1),
            'spam_probability': round(spam_prob, 1),
            'ham_probability': round(ham_prob, 1),
            'confidence': round(max(spam_prob, ham_prob), 1),
            'features': {
                # Structural
                'length': features['length'],
                'word_count': features['word_count'],
                'avg_word_length': round(features.get('avg_word_length', 0), 1),
                # Contact / network indicators
                'has_url': bool(features['has_url']),
                'has_phone': bool(features['has_phone']),
                'has_shortcode': bool(features.get('has_shortcode', 0)),
                'has_email': bool(features.get('has_email', 0)),
                # Money / symbol indicators
                'has_currency': bool(features.get('has_currency', 0)),
                'num_exclamation': features.get('num_exclamation', 0),
                'num_question': features.get('num_question', 0),
                'num_asterisk': features.get('num_asterisk', 0),
                'num_percent': features.get('num_percent', 0),
                # Casing indicators
                'capital_ratio': round(features['capital_ratio'] * 100, 1),
                'num_caps_words': features.get('num_caps_words', 0),
                'has_repeated_chars': bool(features.get('has_repeated_chars', 0)),
                # Keyword group breakdown (8 categories)
                'urgency_count': features.get('urgency_count', 0),
                'prize_count': features.get('prize_count', 0),
                'money_count': features.get('money_count', 0),
                'action_count': features.get('action_count', 0),
                'authority_count': features.get('authority_count', 0),
                'subscription_count': features.get('subscription_count', 0),
                'adult_count': features.get('adult_count', 0),
                'phishing_count': features.get('phishing_count', 0),
                # Overall combined score
                'total_spam_signal_score': features.get('total_spam_signal_score', 0),
                'spam_keywords': features['spam_keyword_count'],
            }
        }
        return jsonify(result)
    
    except FileNotFoundError:
        return jsonify({
            'error': 'Model not trained yet! Please run: python train.py'
        }), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def stats():
    """Return model statistics for the dashboard."""
    try:
        meta = get_metadata()
        if not meta:
            return jsonify({'error': 'No metadata available'}), 404
        
        results = meta.get('results', [])
        model_data = [
            {
                'name': r['name'],
                'accuracy': r['accuracy'],
                'precision': r['precision'],
                'recall': r['recall'],
                'f1_score': r['f1_score'],
                'roc_auc': r.get('roc_auc', r['f1_score']),
                'confusion_matrix': r['confusion_matrix'],
            }
            for r in results
        ]
        
        return jsonify({
            'best_model': meta.get('best_model', 'Unknown'),
            'total_samples': meta.get('total_samples', 0),
            'spam_count': meta.get('spam_count', 0),
            'ham_count': meta.get('ham_count', 0),
            'train_size': meta.get('train_size', 0),
            'test_size': meta.get('test_size', 0),
            'models': model_data
        })
    except FileNotFoundError:
        return jsonify({'error': 'Model not trained'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analytics')
def analytics():
    meta = get_metadata()
    return render_template('analytics.html', metadata=meta)

@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    print("="*50)
    print("  SMS Spam Detector - Starting Flask App")
    print("="*50)
    
    try:
        get_model()
        meta = get_metadata()
        if meta:
            print(f" Model loaded: {meta.get('best_model', 'Unknown')}")
    except FileNotFoundError:
        print("  No trained model found. Run 'python train.py' first.")
    
    print(" Starting server at http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

