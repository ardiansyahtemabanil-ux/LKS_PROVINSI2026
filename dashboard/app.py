import os
import json
import boto3
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)


dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
table = dynamodb.Table('SistemToko-Transactions')


fraud_alerts = []


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SistemToko Dashboard</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <h1 class="mb-4">SistemToko Monitoring Dashboard</h1>
        
        {% if alerts %}
        <div class="alert alert-danger" role="alert">
            <h4 class="alert-heading">⚠️ Deteksi Fraud Baru!</h4>
            <ul>
            {% for alert in alerts %}
                <li>{{ alert }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}

        <div class="card mb-4">
            <div class="card-header bg-primary text-white"><h5>Transaksi Terakhir (DynamoDB)</h5></div>
            <div class="card-body">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Transaction ID</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for tx in transactions %}
                        <tr>
                            <td><code>{{ tx.transaction_id }}</code></td>
                            <td><span class="badge {{ 'bg-danger' if tx.status == 'FRAUD' else 'bg-success' }}">{{ tx.status }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    
    try:
        response = table.scan(Limit=10)
        transactions = response.get('Items', [])
    except Exception as e:
        transactions = []
    
    return render_template_string(HTML_TEMPLATE, transactions=transactions, alerts=fraud_alerts)

@app.route('/webhook', methods=['POST'])
def webhook():

    data = json.loads(request.data)
    
    
    if request.headers.get('X-Amz-Sns-Message-Type') == 'SubscriptionConfirmation':
        return jsonify({"status": "subscribed"}), 200
        
    if 'Message' in data:
        msg = json.loads(data['Message'])
        fraud_alerts.append(f"Transaksi {msg.get('transaction_id')} terindikasi Fraud di lokasi {msg.get('location', 'Unknown')}")
        
    return jsonify({"status": "success"}), 200

@app.route('/report')
def report():
    
    return jsonify({"message": "Athena aggregate analytics query endpoint ready."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)