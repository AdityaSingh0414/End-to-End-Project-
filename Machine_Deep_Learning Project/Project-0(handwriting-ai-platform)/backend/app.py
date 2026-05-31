import os
from flask import Flask, jsonify
from flask_cors import CORS
from routes.api import api_bp

def create_app():
    app = Flask(__name__)
    
    # Enable Cross-Origin Resource Sharing (CORS) for frontend React server integration
    CORS(app)
    
    # Configuration details
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit files to 16MB
    
    # Set up uploads directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    uploads_dir = os.path.join(base_dir, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = uploads_dir

    # Register routes blueprint under prefix /api
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "message": "Handwriting Recognition Platform Backend is online"
        })

    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask server on http://localhost:{port} ...")
    app.run(host='0.0.0.0', port=port, debug=True)
