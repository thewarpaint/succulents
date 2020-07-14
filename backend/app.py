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

@app.route('/v1/payment-intent', methods=['POST'])
def create_payment_intent():
  order_amount = 1234
  order_currency = 'mxn'

  # TODO: Validate data.paymentMethodId
  # data = request.get_json()

  try:
    # Create new PaymentIntent with a PaymentMethod id from the client
    intent = stripe.PaymentIntent.create(
      amount=order_amount,
      currency=order_currency,
      # TODO: Enable paymentMethodId when integrating with the UI
      # payment_method=data['paymentMethodId'],
      payment_method_types=['card'],
      confirmation_method='manual',
      confirm=True,
      # If a mobile client passes `useStripeSdk`, set `use_stripe_sdk=true`
      # to take advantage of new authentication features in mobile SDKs.
      use_stripe_sdk=True if 'useStripeSdk' in data and data['useStripeSdk'] else None,
    )

    return generate_response(intent)
  except stripe.error.CardError as e:
    return jsonify({
      'error': e.user_message
    })

# TODO: Find a better resource path that doesn't have an action
@app.route('/v1/payment-intent/<payment_intent_id>/confirm', methods=['POST'])
def confirm_payment_intent(payment_intent_id):
  # TODO: Validate payment_intent_id
  try:
    # Confirm the PaymentIntent to finalize payment after handling a required action
    # on the client.
    intent = stripe.PaymentIntent.confirm(payment_intent_id)

    return generate_response(intent)
  except stripe.error.CardError as e:
    return jsonify({
      'error': e.user_message
    })

def generate_response(intent):
  status = intent['status']

  if status == 'requires_action' or status == 'requires_source_action':
    # Card requires authentication
    return jsonify({
      'requiresAction': True,
      'paymentIntentId': intent['id'],
      'clientSecret': intent['client_secret']
    })

  if status == 'requires_payment_method' or status == 'requires_source':
    # Card was not properly authenticated, suggest a new payment method
    return jsonify({
      'error': 'Your card was denied, please provide a new payment method'
    })

  if status == 'succeeded':
    # Payment is complete, authentication not required
    # To cancel the payment you will need to issue a Refund (https://stripe.com/docs/api/refunds)
    print('Payment received!')

    return jsonify({
      'clientSecret': intent['client_secret']
    })
