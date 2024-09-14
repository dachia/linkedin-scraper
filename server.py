from flask import Flask, request, send_file
from flask_cors import CORS
import os

from use_cases import scrape_comment_profile

app = Flask(__name__)
CORS(app)

@app.route('/get_csv')
def get_csv():
    # Parse query parameters
    li_at = request.args.get('li_at')
    url = request.args.get('url')

    if not li_at or not url:
        return "Missing required parameters: li_at and url", 400

    scrape_comment_profile(url, li_at)

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
