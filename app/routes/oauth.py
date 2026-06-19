# # routes/oauth.py
# from flask import Blueprint, redirect, url_for, request, session, jsonify
# from ..utils.google_drive import drive_service
# import os

# oauth_bp = Blueprint('oauth', __name__)

# @oauth_bp.route('/authorize')
# def authorize():
#     """Start OAuth2 authorization flow"""
#     auth_url = drive_service.get_authorization_url()
#     return redirect(auth_url)

# @oauth_bp.route('/oauth2callback')
# def oauth2callback():
#     """Handle OAuth2 callback"""
#     # Get the full callback URL
#     authorization_response = request.url
    
#     if drive_service.handle_callback(authorization_response):
#         return redirect(url_for('admin.dashboard'))  # Redirect to your admin dashboard
#     else:
#         return "Authorization failed", 400

# @oauth_bp.route('/check-auth')
# def check_auth():
#     """Check if Google Drive is authenticated"""
#     if drive_service.service:
#         return jsonify({"authenticated": True})
#     else:
#         return jsonify({"authenticated": False, "auth_url": url_for('oauth.authorize', _external=True)})