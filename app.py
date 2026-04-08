import os
import logging
from flask import Flask, request, jsonify
from urllib.parse import urlparse
import requests
import random
import string

# Configure logging
log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO),
                    format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Default request timeout in seconds (configurable via env var)
REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '10'))


def validate_url(url):
    """Validate that the URL uses HTTPS scheme."""
    if not url:
        return False, "URL is empty"
    parsed = urlparse(url)
    if parsed.scheme != 'https':
        return False, f"URL must use HTTPS scheme, got: {parsed.scheme or 'none'}"
    if not parsed.netloc:
        return False, "URL has no host"
    return True, None


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for load balancers and platform probes."""
    return jsonify({"status": "ok"}), 200


@app.route('/modify', methods=['GET'])
def modify_json():
    # Get parameters from the request
    json_url = request.args.get('portainer_template_url')
    new_domain = request.args.get('TRAEFIK_INGRESS_DOMAIN')

    if not json_url or not new_domain:
        return jsonify({"error": "Missing required parameters"}), 400

    # Validate URL scheme
    is_valid, error_msg = validate_url(json_url)
    if not is_valid:
        return jsonify({"error": f"Invalid portainer_template_url: {error_msg}"}), 400

    # Append cache-busting parameter
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    json_url_with_cache = f"{json_url}?cache_bust={random_string}"

    logger.info("Fetching template from upstream URL")
    logger.debug("Upstream URL: %s", json_url_with_cache)

    try:
        # Fetch the JSON file with explicit timeout
        response = requests.get(json_url_with_cache, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        json_content = response.text

        # Replace the variables
        for key, value in request.args.items():
            if key == 'portainer_template_url':
                continue
            placeholder_dollar_brace = '{' + '$' + key + '}'
            json_content = json_content.replace(placeholder_dollar_brace, value)

            placeholder_brace_dollar = '$' + '{' + key + '}'
            json_content = json_content.replace(placeholder_brace_dollar, value)

            logger.debug("Substituted variable: %s", key)

        logger.info("Template processed successfully with %d substitution variables",
                     len(request.args) - 1)  # exclude portainer_template_url
        return json_content, 200, {'Content-Type': 'application/json'}

    except requests.Timeout:
        logger.error("Upstream request timed out after %d seconds", REQUEST_TIMEOUT)
        return jsonify({"error": "Upstream request timed out"}), 504

    except requests.RequestException as e:
        logger.error("Failed to fetch upstream template: %s", str(e))
        return jsonify({"error": f"Failed to fetch JSON: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info("Starting template server on port %d", port)
    app.run(host='0.0.0.0', port=port)
