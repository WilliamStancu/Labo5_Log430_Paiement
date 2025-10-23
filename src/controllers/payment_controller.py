"""
Payment controller
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import numbers
import requests
from commands.write_payment import create_payment, update_status_to_paid
from queries.read_payment import get_payment_by_id

def get_payment(payment_id):
    return get_payment_by_id(payment_id)

def add_payment(request):
    """ Add payment based on given params """
    payload = request.get_json() or {}
    user_id = payload.get('user_id')
    order_id = payload.get('order_id')
    total_amount = payload.get('total_amount')
    result = create_payment(order_id, user_id, total_amount)
    if isinstance(result, numbers.Number):
        return {"payment_id": result}
    else:
        return {"error": str(result)}
    
def process_payment(payment_id, credit_card_data):
    """ Process payment with given ID, notify store_manager sytem that the order is paid """
    # S'il s'agissait d'une véritable API de paiement, nous enverrions les données de la carte de crédit à un payment gateway (ex. Stripe, Paypal) pour effectuer le paiement. Cela pourrait se trouver dans un microservice distinct.
    _process_credit_card_payment(credit_card_data)

    # Si le paiement est réussi, mettre à jour le statut du paiement localement
    update_result = update_status_to_paid(payment_id)
    print(f"Updated order {update_result['order_id']} to paid={update_result}")

    # Appel du service Store Manager pour mettre à jour la commande (is_paid à true)
    order_id = update_result["order_id"]
    try:
        store_manager_url = "http://store_manager:5000/orders"
        payload = {"order_id": order_id, "is_paid": True}
        headers = {"Content-Type": "application/json"}
        response = requests.put(store_manager_url, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        print(f"PUT /orders Store Manager response: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la commande dans Store Manager: {e}")

    result = {
        "order_id": update_result["order_id"],
        "payment_id": update_result["payment_id"],
        "is_paid": update_result["is_paid"]
    }

    return result
    
def _process_credit_card_payment(payment_data):
    """ Placeholder method for simulated credit card payment """
    print(payment_data.get('cardNumber'))
    print(payment_data.get('cardCode'))
    print(payment_data.get('expirationDate'))