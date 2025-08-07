from app import app
import admin_comprehensive
import routes
import enhanced_routes
import nft_routes
import admin_advanced
import salary_routes
import otp_routes
from support_responses import support_responses_bp
from flask import jsonify

# Register blueprint
app.register_blueprint(support_responses_bp)

@app.route('/robots.txt')
def robots_txt():
    """Robots.txt for SEO"""
    return "User-agent: *\nDisallow: /admin\nDisallow: /admin-access"

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Page not found',
        'message': 'The requested URL was not found on the server'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on our end'
    }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
