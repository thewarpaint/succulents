#! /usr/bin/env python3

# See https://github.com/stripe-samples/accept-a-card-payment/blob/master/without-webhooks/server/python/server.py
import stripe
import json
import os

from dotenv import load_dotenv, find_dotenv
from flask import Flask, render_template, jsonify, request, send_from_directory

# Setup Stripe python client library
load_dotenv(find_dotenv())
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = os.getenv('STRIPE_API_VERSION')

static_dir = str(os.path.abspath(os.path.join(__file__ , '..', os.getenv('STATIC_DIR'))))
app = Flask(__name__, static_folder=static_dir,
            static_url_path="", template_folder=static_dir)

@app.route('/v1/configuration', methods=['GET'])
def get_configuration():
  # Send publishable key to client
  return jsonify({
    'publishableKey': os.getenv('STRIPE_PUBLISHABLE_KEY')
  })
