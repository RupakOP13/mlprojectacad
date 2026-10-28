"""
SMS Spam Detector - Model Training Module
Trains multiple classifiers and selects the best one
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
from sklearn.calibration import CalibratedClassifierCV
import warnings
warnings.filterwarnings('ignore')

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
os.makedirs(MODELS_DIR, exist_ok=True)


def build_pipelines():
    """Build ML pipelines for each classifier."""
    pipelines = {
        'Naive Bayes': Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 2),
                sublinear_tf=True,
                min_df=2
            )),
            ('clf', MultinomialNB(alpha=0.1))
        ]),
        'Logistic Regression': Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 2),
                sublinear_tf=True,
                min_df=2
            )),
            ('clf', LogisticRegression(C=1.0, max_iter=1000, random_state=42))
        ]),
        'SVM': Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=10000,
                ngram_range=(1, 2),
                sublinear_tf=True,
                min_df=2
            )),
            ('clf', CalibratedClassifierCV(SVC(kernel='linear', C=1.0, random_state=42)))
        ]),
        'Random Forest': Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                sublinear_tf=True,
                min_df=2
            )),
            ('clf', RandomForestClassifier(
                n_estimators=200,
                max_depth=None,
                random_state=42,
                n_jobs=-1
            ))
        ])
    }
    return pipelines


def evaluate_model(model, X_test, y_test, model_name):
    """Evaluate a trained model and return metrics."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
    
    metrics = {
        'name': model_name,
        'accuracy': round(accuracy_score(y_test, y_pred) * 100, 2),
        'precision': round(precision_score(y_test, y_pred) * 100, 2),
        'recall': round(recall_score(y_test, y_pred) * 100, 2),
        'f1_score': round(f1_score(y_test, y_pred) * 100, 2),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'classification_report': classification_report(y_test, y_pred, target_names=['Ham', 'Spam']),
        'y_pred': y_pred.tolist(),
        'y_test': y_test.tolist()
    }
    
    if y_proba is not None:
        metrics['roc_auc'] = round(roc_auc_score(y_test, y_proba) * 100, 2)
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        metrics['fpr'] = fpr.tolist()
        metrics['tpr'] = tpr.tolist()
    else:
        metrics['roc_auc'] = metrics['f1_score']
    
    return metrics


def train_all_models(df):
    """Train all models, evaluate, and save the best one."""
    X = df['cleaned']
    y = df['label_num']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    pipelines = build_pipelines()
    results = []
    trained_models = {}
    
    print(f"\n{'='*60}")
    print("TRAINING & EVALUATING MODELS")
    print(f"{'='*60}")
    print(f"Train size: {len(X_train)} | Test size: {len(X_test)}\n")
    
    for name, pipeline in pipelines.items():
        print(f"Training {name}...", end=' ', flush=True)
        pipeline.fit(X_train, y_train)
        metrics = evaluate_model(pipeline, X_test, y_test, name)
        results.append(metrics)
        trained_models[name] = pipeline
        
        print(f"Done! | Acc: {metrics['accuracy']}% | F1: {metrics['f1_score']}% | ROC-AUC: {metrics['roc_auc']}%")
    
    print(f"\n{'='*60}")
    print("MODEL COMPARISON SUMMARY")
    print(f"{'='*60}")
    print(f"{'Model':<22} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10} {'ROC-AUC':>10}")
    print('-'*72)
    for r in results:
        print(f"{r['name']:<22} {r['accuracy']:>9}% {r['precision']:>9}% {r['recall']:>9}% {r['f1_score']:>9}% {r['roc_auc']:>9}%")
    
    # Select best model by F1 score
    best = max(results, key=lambda x: x['f1_score'])
    best_model = trained_models[best['name']]
    print(f"\n[OK] Best Model: {best['name']} (F1: {best['f1_score']}%)")
    
    # Save best model and vectorizer
    model_path = os.path.join(MODELS_DIR, 'best_model.pkl')
    joblib.dump(best_model, model_path)
    print(f"[OK] Model saved to: {model_path}")
    
    # Save all models
    for name, model in trained_models.items():
        safe_name = name.lower().replace(' ', '_')
        joblib.dump(model, os.path.join(MODELS_DIR, f'{safe_name}.pkl'))
    
    # Save metadata
    metadata = {
        'best_model': best['name'],
        'results': results,
        'train_size': len(X_train),
        'test_size': len(X_test),
        'total_samples': len(df),
        'spam_count': int(df['label_num'].sum()),
        'ham_count': int((df['label_num'] == 0).sum())
    }
    joblib.dump(metadata, os.path.join(MODELS_DIR, 'metadata.pkl'))
    
    return best_model, results, metadata


def load_best_model():
    """Load the best trained model."""
    model_path = os.path.join(MODELS_DIR, 'best_model.pkl')
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No trained model found at {model_path}. Run train.py first.")
    return joblib.load(model_path)


def load_metadata():
    """Load training metadata."""
    meta_path = os.path.join(MODELS_DIR, 'metadata.pkl')
    if not os.path.exists(meta_path):
        return None
    return joblib.load(meta_path)

