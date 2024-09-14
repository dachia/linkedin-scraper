from flask import Flask, request, send_file
from flask_cors import CORS
import os

from use_cases import scrape_comment_profile

app = Flask(__name__)
CORS(app)

@app.route('/scrape-commenters')
def scrape_commenters():
    # Parse query parameters
    li_at = request.args.get('li_at')
    url = request.args.get('url')
    user_agent = request.args.get('user_agent')

    if not li_at or not url or not user_agent:
        return "Missing required parameters: li_at, url, and user_agent", 400

    scrape_comment_profile(url, li_at, user_agent)

    # Check if the CSV file exists
    csv_file = 'linkedin_profiles.csv'
    if not os.path.exists(csv_file):
        return "CSV file not found", 404

    # Send the CSV file
    return send_file(csv_file, 
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=csv_file)

if __name__ == "__main__":
    app.run(port=8000, debug=True)
