#!/usr/bin/env python3
"""
Authentication service for Cloud Health Dashboard Phase 2
Handles user authentication, JWT token management, and authorization
"""

from flask import request, jsonify
from functools import wraps
import jwt
import bcrypt
from datetime import datetime, timedelta
from app import app, db, User

def generate_token(user_id, username, role):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24),  # 24 hour expiration
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_password(password, password_hash):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
            
            # Update last login
            current_user.last_login = datetime.utcnow()
            db.session.commit()
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user or current_user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def operator_required(f):
    """Decorator to require operator or admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user or current_user.role not in ['admin', 'operator']:
                return jsonify({'error': 'Operator or admin access required'}), 403
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# Authentication routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not verify_password(data['password'], user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate token
    token = generate_token(user.id, user.username, user.role)
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        },
        'expires_in': 86400  # 24 hours in seconds
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    password_hash = hash_password(data['password'])
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=password_hash,
        role=data.get('role', 'user')
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Generate token for new user
    token = generate_token(user.id, user.username, user.role)
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        },
        'expires_in': 86400
    }), 201

@app.route('/api/auth/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user profile"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role,
        'created_at': current_user.created_at.isoformat(),
        'last_login': current_user.last_login.isoformat() if current_user.last_login else None
    })

@app.route('/api/auth/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update current user profile"""
    data = request.get_json()
    
    if 'email' in data:
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != current_user.id:
            return jsonify({'error': 'Email already exists'}), 400
        current_user.email = data['email']
    
    if 'password' in data and data['password']:
        current_user.password_hash = hash_password(data['password'])
    
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'})

@app.route('/api/auth/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    """Refresh JWT token"""
    token = generate_token(current_user.id, current_user.username, current_user.role)
    
    return jsonify({
        'token': token,
        'expires_in': 86400
    })

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    """User logout endpoint"""
    # In a real application, you might want to blacklist the token
    # For now, we'll just return a success message
    return jsonify({'message': 'Logged out successfully'})
