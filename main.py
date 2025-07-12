# # main.py
# import os
# from flask import jsonify, request
# from werkzeug.utils import secure_filename

# # Import your existing function
# from stringart_public import generate_string_art

# def process_image_request(request):
#     """
#     HTTP-triggered cloud function that wraps the string art engine.
#     1. Validates the request.
#     2. Saves the uploaded image to a temporary location.
#     3. Calls the core string art generation logic.
#     4. Returns the results as a JSON response.
#     """
#     # --- 1. Validate the request ---
#     if request.method != 'POST':
#         return 'Only POST requests are accepted', 405

#     if 'image' not in request.files:
#         return 'Missing "image" file in the request', 400

#     uploaded_file = request.files['image']
#     if uploaded_file.filename == '':
#         return 'No selected file', 400

#     # --- 2. Save image to the temporary directory ---
#     # Cloud Functions can only write to the /tmp directory
#     filename = secure_filename(uploaded_file.filename)
#     temp_path = os.path.join('/tmp', filename)
#     uploaded_file.save(temp_path)

#     # --- 3. Call your engine ---
#     try:
#         results = generate_string_art(temp_path)
#     except Exception as e:
#         # If your engine fails, return a server error
#         print(f"Error during string art generation: {e}")
#         return "Internal server error during image processing", 500
#     finally:
#         # --- 4. Clean up the temporary file ---
#         if os.path.exists(temp_path):
#             os.remove(temp_path)

#     # --- 5. Return JSON response ---
#     return jsonify(results)

# Conver to logger
# main.py
import json
from flask import request

def process_image_request(request):
    """
    Temporarily acts as a logger to capture the webhook data from Shopify.
    """
    # Check if the request has JSON data
    if request.is_json:
        webhook_data = request.get_json()
        
        # Print the entire data structure to the logs
        print("--- Received Shopify Webhook Data ---")
        print(json.dumps(webhook_data, indent=2))
        print("------------------------------------")

        return "Webhook data received and logged.", 200
    
    return "No JSON data received.", 400