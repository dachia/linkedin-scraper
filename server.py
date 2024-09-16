from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import os

from use_cases import scrape_comment_profile, auto_connect_profiles, configure_search_filters, scrape_search_results

app = Flask(__name__)
CORS(app)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    action = data.get('action')
    li_at = data.get('li_at')
    url = data.get('url')
    user_agent = data.get('user_agent')

    if not all([action, li_at, url, user_agent]):
        return jsonify({"error": "Missing required parameters"}), 400

    if action == "scrapeCommenters":
        scrape_comment_profile(url, li_at, user_agent)
        csv_file = 'linkedin_profiles.csv'
        if not os.path.exists(csv_file):
            return jsonify({"error": "CSV file not found"}), 404
        return send_file(csv_file, 
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name=csv_file)
    elif action == "autoConnect":
        result = auto_connect_profiles(url, li_at, user_agent)
        return jsonify(result)
    elif action == "configureFilters":
        filters = data.get('filters', {})
        result = configure_search_filters(url, li_at, user_agent, filters)
        return jsonify(result)
    elif action == "scrapeSearchResults":
        result = scrape_search_results(url, li_at, user_agent)
        if result["success"]:
            csv_file = 'linkedin_profile_links.csv'
            if not os.path.exists(csv_file):
                return jsonify({"error": "CSV file not found"}), 404
            return send_file(csv_file, 
                             mimetype='text/csv',
                             as_attachment=True,
                             download_name=csv_file)
        else:
            return jsonify(result), 400
    else:
        return jsonify({"error": "Invalid action"}), 400

if __name__ == "__main__":
    app.run(port=8000, debug=True)
