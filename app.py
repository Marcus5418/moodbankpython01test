from flask import Flask, render_template, request, jsonify, session
import json
import datetime
import uuid
from collections import defaultdict
import os

app = Flask(__name__)
app.secret_key = 'moodbank_secret_key_2024'

# In-memory storage (in production, use a proper database)
mood_entries = []
user_profiles = {}

# Emotional solutions database
EMOTIONAL_SOLUTIONS = {
    'anxiety': {
        'techniques': [
            'Deep breathing exercises (4-7-8 technique)',
            'Progressive muscle relaxation',
            'Mindfulness meditation',
            'Grounding techniques (5-4-3-2-1 method)',
            'Gentle physical exercise like walking'
        ],
        'affirmations': [
            'I am safe and in control of my breathing',
            'This feeling will pass, and I am stronger than my anxiety',
            'I choose peace and calm in this moment',
            'I trust in my ability to handle whatever comes my way'
        ],
        'activities': [
            'Listen to calming music or nature sounds',
            'Practice yoga or gentle stretching',
            'Write in a journal about your feelings',
            'Call a trusted friend or family member',
            'Take a warm bath or shower'
        ]
    },
    'depression': {
        'techniques': [
            'Cognitive behavioral therapy techniques',
            'Behavioral activation (scheduling pleasant activities)',
            'Gratitude journaling',
            'Social connection and support',
            'Regular sleep schedule maintenance'
        ],
        'affirmations': [
            'I am worthy of love and happiness',
            'Small steps forward are still progress',
            'I have overcome challenges before and I can do it again',
            'My feelings are valid, and it\'s okay to not be okay sometimes'
        ],
        'activities': [
            'Engage in a creative hobby',
            'Spend time in nature or sunlight',
            'Practice self-care routines',
            'Connect with supportive people',
            'Set small, achievable daily goals'
        ]
    },
    'stress': {
        'techniques': [
            'Time management and prioritization',
            'Stress inoculation training',
            'Relaxation response techniques',
            'Problem-solving strategies',
            'Boundary setting practices'
        ],
        'affirmations': [
            'I can handle this one step at a time',
            'I have the skills and resources to manage stress',
            'It\'s okay to ask for help when I need it',
            'I choose to focus on what I can control'
        ],
        'activities': [
            'Take regular breaks throughout the day',
            'Practice time-blocking for tasks',
            'Engage in physical exercise',
            'Practice saying no to additional commitments',
            'Create a calming evening routine'
        ]
    },
    'anger': {
        'techniques': [
            'Anger management breathing techniques',
            'Cognitive restructuring',
            'Assertiveness training',
            'Conflict resolution skills',
            'Emotional regulation strategies'
        ],
        'affirmations': [
            'I can express my feelings in healthy ways',
            'I choose to respond rather than react',
            'My anger is information about my needs',
            'I am in control of my actions and responses'
        ],
        'activities': [
            'Physical exercise to release tension',
            'Write about your feelings before responding',
            'Practice active listening in conversations',
            'Take a timeout when feeling overwhelmed',
            'Use humor to defuse tense situations'
        ]
    },
    'sadness': {
        'techniques': [
            'Emotional processing and acceptance',
            'Meaning-making activities',
            'Social support seeking',
            'Self-compassion practices',
            'Grief processing techniques'
        ],
        'affirmations': [
            'It\'s natural and healthy to feel sad sometimes',
            'I allow myself to feel and process my emotions',
            'This sadness will not last forever',
            'I am compassionate with myself during difficult times'
        ],
        'activities': [
            'Allow yourself to cry if needed',
            'Reach out to supportive friends or family',
            'Engage in comforting activities',
            'Practice self-care and gentleness',
            'Consider professional support if needed'
        ]
    }
}

def get_user_id():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

def analyze_mood_pattern(user_id):
    user_entries = [entry for entry in mood_entries if entry.get('user_id') == user_id]
    if not user_entries:
        return None
    
    # Get recent entries (last 7 days)
    recent_entries = sorted(user_entries, key=lambda x: x['timestamp'], reverse=True)[:7]
    
    mood_counts = defaultdict(int)
    emotion_counts = defaultdict(int)
    
    for entry in recent_entries:
        mood_counts[entry['mood']] += 1
        for emotion in entry['emotions']:
            emotion_counts[emotion] += 1
    
    dominant_mood = max(mood_counts, key=mood_counts.get) if mood_counts else None
    dominant_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return {
        'dominant_mood': dominant_mood,
        'dominant_emotions': [emotion for emotion, count in dominant_emotions],
        'total_entries': len(recent_entries),
        'mood_distribution': dict(mood_counts)
    }

def get_personalized_solutions(emotions):
    solutions = {
        'techniques': [],
        'affirmations': [],
        'activities': []
    }
    
    for emotion in emotions:
        if emotion in EMOTIONAL_SOLUTIONS:
            emotion_solutions = EMOTIONAL_SOLUTIONS[emotion]
            solutions['techniques'].extend(emotion_solutions['techniques'][:2])
            solutions['affirmations'].extend(emotion_solutions['affirmations'][:2])
            solutions['activities'].extend(emotion_solutions['activities'][:2])
    
    # Remove duplicates while preserving order
    for key in solutions:
        solutions[key] = list(dict.fromkeys(solutions[key]))
    
    return solutions

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/track')
def track():
    return render_template('track.html')

@app.route('/insights')
def insights():
    user_id = get_user_id()
    pattern = analyze_mood_pattern(user_id)
    return render_template('insights.html', pattern=pattern)

@app.route('/solutions')
def solutions():
    return render_template('solutions.html')

@app.route('/api/mood', methods=['POST'])
def save_mood():
    user_id = get_user_id()
    data = request.json
    
    mood_entry = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'mood': data['mood'],
        'emotions': data['emotions'],
        'intensity': data['intensity'],
        'notes': data.get('notes', ''),
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    mood_entries.append(mood_entry)
    
    return jsonify({'success': True, 'id': mood_entry['id']})

@app.route('/api/moods')
def get_moods():
    user_id = get_user_id()
    user_entries = [entry for entry in mood_entries if entry.get('user_id') == user_id]
    return jsonify(sorted(user_entries, key=lambda x: x['timestamp'], reverse=True))

@app.route('/api/solutions/<emotions>')
def get_solutions(emotions):
    emotion_list = emotions.split(',')
    solutions = get_personalized_solutions(emotion_list)
    return jsonify(solutions)

@app.route('/api/insights')
def get_insights():
    user_id = get_user_id()
    pattern = analyze_mood_pattern(user_id)
    return jsonify(pattern)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
