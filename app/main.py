from flask import Flask, Blueprint, request, jsonify
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
main = Blueprint('main', __name__)

csv_data = None

@main.route('/upload', methods=['POST'])
def upload_file():
    global csv_data
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join('/tmp', filename)
        file.save(filepath)
        
        csv_data = pd.read_csv(filepath)
        return jsonify({'message': 'Upload successful'})
    else:
        return jsonify({'error': 'Invalid file format'}), 400

@main.route('/list_records', methods=['GET'])
def list_records():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if csv_data is None:
        return jsonify({'error': 'No CSV file has been uploaded yet'}), 404
    
    # Pagination
    start = (page - 1) * per_page
    end = page * per_page
    paginated_data = csv_data.iloc[start:end]

    records = paginated_data.to_dict(orient='records')
    return jsonify({
        'page': page,
        'per_page': per_page,
        'total': len(csv_data),
        'total_pages': (len(csv_data) + per_page - 1) // per_page,
        'data': records
    })

app.register_blueprint(main)

if __name__ == '__main__':
    app.run(debug=True)
