def Add_notification(self, data, files=None):
        # Create a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            notification_ref = self.db.collection('notification_mst')
            
            # Ensure necessary data is present
            if not all(key in data for key in ['notification_title', 'notification_comment']):
                raise ValueError("Missing required information")
            
            # Initialize variables for file details
            storage_file_name = None
            file_url = None
            
             # If a file is provided, upload it to Firebase Storage
            if files:
                # Get the file name and content
                file_name = files.filename
                file_content = files.read()  # Read the file content

                # Create a custom file name and path in the "notification" folder
                storage_file_name = f"notification/{timestamp}_{file_name}"
                
                # Upload the file to Firebase Storage
                bucket = storage.bucket()
                blob = bucket.blob(storage_file_name)
                blob.upload_from_string(file_content, content_type=files.content_type)

                # Get the public URL of the uploaded file
                file_url = blob.public_url
                
                # Include file name in the notification data
                notification_file_name = f"{timestamp}_{file_name}"
            else:
                # No file provided, set to None
                notification_file_name = None
            
            # Create custom document ID 
            doc_id= timestamp
            # Save file names in Firestore, using None for fields that have no associated file
            notification_data = {
                'notification_title': data["notification_title"],
                'notification_comment': data["notification_comment"],
                'notification_start_date': data["notification_start_date"],
                'notification_end_date': data["notification_end_date"],
                # Set file fields in the database
                'notification_file_name': notification_file_name
            }

            # Add data to Firestore with custom document ID
            notification_ref.document(doc_id).set(notification_data)
            return {'status': 'success', 'message': 'Notification Save Successfully'}, 200
            
        except Exception as e:
            logger.error(f"Error add notification: {e}")
            return {'status': 'error', 'message': str(e)}, 500
    
    def fetch_all_notification(self, query_params=None):
        try:
            # Start query from 'notification_mst' collection
            query = self.db.collection('notification_mst')

            # Apply filters based on query parameters
            if query_params:
                if 'notification_start_date' in query_params:
                    query = query.where('notification_start_date', '>=', query_params.get('notification_start_date'))

                if 'notification_end_date' in query_params:
                    query = query.where('notification_end_date', '<=', query_params.get('notification_end_date'))
                    
                if 'notification_title' in query_params:
                    title = query_params.get('notification_title')
                    # query = query.where('notification_title', '==', query_params.get('notification_title'))
                    query = query.where('notification_title', '>=', title).where('notification_title', '<', title + '\uf8ff')
            
            # Calculate the total number of documents before applying pagination
            all_docs = list(query.stream())
            total_count = len(all_docs)

            # Set pagination defaults
            page = int(query_params.get('page', 1)) if query_params else 1
            limit = int(query_params.get('limit', 10)) if query_params else 10
            offset = (page - 1) * limit

            # Apply pagination using offset and limit
            query = query.offset(offset).limit(limit)
            paginated_docs = query.stream()
            
            # Fetch the paginated documents and prepare the response
            notifications = []
            for notification_doc in paginated_docs:
                notification_data = notification_doc.to_dict()
                notification_data['document_id'] = notification_doc.id  # Add document ID
                notification_data['total_count'] = total_count  # Add total count
                notifications.append(notification_data)

            # Return the notifications and a 200 status
            return notifications, 200

        except Exception as e:
            logger.error(f"Error fetching logs data: {e}")
            return {'error': 'Internal Server Error'}, 500
        
    def fetch_notification(self, id):
        try:
            product_ref = self.db.collection('notification_mst').document(id)
            product = product_ref.get()
            return product.to_dict(), 200
        except Exception as e:
            print("Error fetching user:", e)
            return {'error': 'Internal Server Error'}, 500
        
    def update_notification(self, document_id, data,file):
        
        # Create a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            notification_ref = self.db.collection('notification_mst')
            notification_doc = notification_ref.document(document_id)

            # Check if the document exists
            if not notification_doc.get().exists:
                return {'error': 'Data not found'}, 404
            
            # Initialize variables for file details
            storage_file_name = None
            file_url = None
            
            # If a file is provided, upload it to Firebase Storage
            if file:
                # Get the file name and content
                file_name = file.filename
                file_content = file.read()  # Read the file content

                # Create a custom file name and path in the "notification" folder
                storage_file_name = f"notification/{timestamp}_{file_name}"
                
                # Upload the file to Firebase Storage
                bucket = storage.bucket()
                blob = bucket.blob(storage_file_name)
                blob.upload_from_string(file_content, content_type=file.content_type)

                # Get the public URL of the uploaded file
                file_url = blob.public_url
                
                # Include file name in the notification data
                notification_file_name = f"{timestamp}_{file_name}"
            else:
                 # No file provided, retrieve the existing file name from the document
                existing_data = notification_doc.get().to_dict()
                notification_file_name = existing_data.get('notification_file_name', None)
                file_url = existing_data.get('notification_file_url', None)  # If you previously stored the URL in 'notification_file_url'

            # Update the user document with the new data
            notification_doc.update({
                'notification_comment': data.get('notification_comment'),               
                'notification_end_date': data.get('notification_end_date')  ,             
                'notification_start_date': data.get('notification_start_date'),               
                'notification_title': data.get('notification_title'),   
                'notification_file_name': notification_file_name,            
            })

            return {'message': 'User updated successfully'}, 200

        except Exception as e:
            return {'error': str(e)}, 500
        
        
    def delete_file(self, document_id):

        try:
            notification_ref = self.db.collection('notification_mst')
            notification_doc = notification_ref.document(document_id)

            # Check if the document exists
            if not notification_doc.get().exists:
                return {'error': 'Data not found'}, 404

            # Update the specific document, not the collection
            notification_doc.update({'notification_file_name': None})

            return {'message': 'File deleted successfully'}, 200

        except Exception as e:
            return {'error': str(e)}, 500
        
    def delete_document(self, document_id):
        try:
            notification_ref = self.db.collection('notification_mst')
            notification_doc = notification_ref.document(document_id)

            # Check if the document exists
            if not notification_doc.get().exists:
                return {'error': 'Document not found'}, 404

            # Delete the document
            notification_doc.delete()

            return {'message': 'Document deleted successfully'}, 200

        except Exception as e:
            return {'error': str(e)}, 500
        
        
    def notification_download(self, filename):
        try:
            bucket = storage.bucket()
            blob = bucket.blob(f'notification/{filename}')

            # Check if the file exists
            if not blob.exists():
                return jsonify({"error": "File not found"}), 404

            # Download the file locally
            local_folder = "downloads"
            os.makedirs(local_folder, exist_ok=True)
            local_file_path = os.path.join(local_folder, filename)
            blob.download_to_filename(local_file_path)

            # Serve the file for download
            return send_file(local_file_path, as_attachment=True, download_name=filename), 200

        except Exception as e:
            return {'error': str(e)}, 500
