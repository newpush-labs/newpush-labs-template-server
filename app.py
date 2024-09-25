import os
from flask import Flask, request, jsonify
import requests
import random
import string

app = Flask(__name__)

@app.route('/modify', methods=['GET'])
def modify_json():
    # Get parameters from the request
    json_url = request.args.get('portainer_template_url')
    new_domain = request.args.get('TRAEFIK_INGRESS_DOMAIN')
    
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    json_url = f"{json_url}?cache_bust={random_string}"

    print("Fetching JSON from:", json_url)
    print("New domain:", new_domain)
    
    if not json_url or not new_domain:
        return jsonify({"error": "Missing required parameters"}), 400
    
    try:
        # Fetch the JSON file
        response = requests.get(json_url)
        response.raise_for_status()
        json_content = response.text
        
        # Replace the variables 
        for key, value in request.args.items():
            placeholder = '{'+'$'+key+'}'
            print(f"Replacing {placeholder} with {value}")
            json_content = json_content.replace(placeholder, value)

            placeholder = '$'+'{'+key+'}'
            print(f"Replacing {placeholder} with {value}")
            json_content = json_content.replace(placeholder, value)
            # print(json_content)
        
        return json_content, 200, {'Content-Type': 'application/json'}
    
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to fetch JSON: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)