from notification import Notification
notification = Notification()
@app.route('/api/notification', methods=['POST'])
def send_notification():
    data = flask.request.form.to_dict()
    files = flask.request.files.get('file')  # Get the list of uploaded files
    response, status = notification.Add_notification(data, files)
    return flask.jsonify(response), status

@app.route('/api/notification/list', methods=['GET'])
def fetch_all_notification_data():
    query_params = flask.request.args
    response, status = notification.fetch_all_notification(query_params)
    return flask.jsonify(response), status

@app.route('/api/notification/download/<filename>', methods=['GET'])
def notification_download(filename):
    return notification.notification_download(filename)

@app.route('/api/notification/<id>', methods=['GET'])
def fetch_notification(id):
    response, status = notification.fetch_notification(id)
    return flask.jsonify(response), status

@app.route('/api/notification/update/<uid>', methods=['PUT'])
def update_notification(uid):

    token = flask.request.headers.get('Authorization')      
    # Check if token exists
    if token is None:
        return flask.jsonify({'error': 'Token is missing'}), 401
    
    token = token.split()[1]
    login_id = authenticaion.verify_jwt_token(token)
    if login_id:        

        data = flask.request.form
        file = flask.request.files.get('notification_file_name')
        response, status = notification.update_notification(uid, data,file)
        return flask.jsonify(response), status

    else:
        return flask.jsonify({'error': 'Invalid or expired token'}), 401 
