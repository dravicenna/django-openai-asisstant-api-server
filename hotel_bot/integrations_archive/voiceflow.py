"""
Using Voiceflow Endpoints with Authentication

To interact with the Voiceflow endpoints, you need to ensure proper authentication. 
This involves setting the X-API-KEY in the request header and using a secret CUSTOM_API_KEY 
within your Replit template. Follow these steps for successful authorization:

1. Set CUSTOM_API_KEY:
   - In your Replit template, define a variable `CUSTOM_API_KEY` with your secret API key. 
     This key is crucial for the authentication process.

2. Choose a Password:
   - Select any password of your choice. This password will be used as the value for the `X-API-KEY`  in the request header. It's important to always include this in the header of every request you make.

3. Setup and connect the Voiceflow template:
   - You can get access to the Voiceflow template directly from within our resource hub: https://hub.integraticus.com/lead-gen-chatbot-template/ (It's free)

4. Set Headers for the Request:
   - In your request headers, include the following: 'X-API-KEY': [Your chosen password]
"""

import logging

from flask import jsonify, request

import hotel_bot.utils as utils

# Configure logging for this module
logging.basicConfig(level=logging.INFO)


# Defines if a DB mapping is required
def requires_mapping():
    return False


def setup_routes(app, client, tool_data, assistant_id):
    # Check OpenAI version compatibility
    utils.check_openai_version()

    # Route to start the conversation
    @app.route('/voiceflow/start', methods=['GET'])
    def start_conversation():
        utils.check_api_key()  # Check the API key
        logging.info('Starting a new conversation...')
        thread = client.beta.threads.create()
        logging.info(f'New thread created with ID: {thread.id}')
        return jsonify({'thread_id': thread.id})

    # Route to chat with the assistant
    @app.route('/voiceflow/chat', methods=['POST'])
    def chat():
        utils.check_api_key()  # Check the API key
        data = request.json
        thread_id = data.get('thread_id')
        user_input = data.get('message', '')

        if not thread_id:
            logging.error('Error: Missing thread_id')
            return jsonify({'error': 'Missing thread_id'}), 400

        logging.info(f'Received message: {user_input} for thread ID: {thread_id}')
        client.beta.threads.messages.create(thread_id=thread_id, role='user', content=user_input)
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
        # This processes any possible action requests
        utils.process_tool_calls(client, thread_id, run.id, tool_data)

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        response = messages.data[0].content[0].text.value
        logging.info(f'Assistant response: {response}')
        return jsonify({'response': response})
