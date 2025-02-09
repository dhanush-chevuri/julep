# -*- coding: utf-8 -*-
"""E-commerce_Order_Processing_Workflow.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1mP-uZV8-wMMJA0eDcF5TH6C82ZOup055
"""

import uuid
import yaml
import time
from julep import Client

AGENT_UUID = uuid.uuid4()
ORDER_PLACEMENT_TASK_UUID = uuid.uuid4()
INVENTORY_CHECK_TASK_UUID = uuid.uuid4()
PAYMENT_PROCESSING_TASK_UUID = uuid.uuid4()
SHIPMENT_TRACKING_TASK_UUID = uuid.uuid4()

api_key = ""  # Your API key here
client = Client(api_key=api_key, environment="dev")

agent = client.agents.create_or_update(
    agent_id=AGENT_UUID,
    name="Order Processing Assistant",
    about="An AI agent specialized in automating the order processing workflow for e-commerce.",
    model="gpt-4o",
)

order_placement_task_def = yaml.safe_load("""
name: Order Placement

input_schema:
  type: object
  properties:
    user_id:
      type: string
    order_details:
      type: object
      properties:
        item_id:
          type: integer
        quantity:
          type: integer

main:
- prompt:
  - role: system
    content: >-
      You are an order placement assistant. Process the following order:
      User ID: {{inputs[0].user_id}}
      Order Details: {{inputs[0].order_details}}

      Confirm the order placement and return the order ID.
  unwrap: true

- evaluate:
    order_id: _.uuid()

- return:
    order_id: _
""")

order_placement_task = client.tasks.create_or_update(
    task_id=ORDER_PLACEMENT_TASK_UUID,
    agent_id=AGENT_UUID,
    **order_placement_task_def
)

inventory_check_task_def = yaml.safe_load("""
name: Inventory Check

input_schema:
  type: object
  properties:
    item_id:
      type: integer
    quantity:
      type: integer

main:
- prompt:
  - role: system
    content: >-
      You are an inventory checker. Check the availability of the following item:
      Item ID: {{inputs[0].item_id}}
      Quantity Requested: {{inputs[0].quantity}}

      Return true if available, otherwise return false.
  unwrap: true
""")

inventory_check_task = client.tasks.create_or_update(
    task_id=INVENTORY_CHECK_TASK_UUID,
    agent_id=AGENT_UUID,
    **inventory_check_task_def
)

payment_processing_task_def = yaml.safe_load("""
name: Payment Processing

input_schema:
  type: object
  properties:
    user_id:
      type: string
    order_id:
      type: string
    amount:
      type: number

main:
- prompt:
  - role: system
    content: >-
      You are a payment processor. Process payment for the following order:
      User ID: {{inputs[0].user_id}}
      Order ID: {{inputs[0].order_id}}
      Amount: {{inputs[0].amount}}

      Confirm payment status (success or failure).
  unwrap: true

- evaluate:
    payment_status: "success"  # Simulating a successful payment

- return:
    payment_status: _
""")

payment_processing_task = client.tasks.create_or_update(
    task_id=PAYMENT_PROCESSING_TASK_UUID,
    agent_id=AGENT_UUID,
    **payment_processing_task_def
)

shipment_tracking_task_def = yaml.safe_load("""
name: Shipment Tracking

input_schema:
  type: object
  properties:
    order_id:
      type: string

main:
- prompt:
  - role: system
    content: >-
      You are a shipment tracker. Track the shipment for the following order:
      Order ID: {{inputs[0].order_id}}

      Return the current status of the shipment.
  unwrap: true
""")

shipment_tracking_task = client.tasks.create_or_update(
    task_id=SHIPMENT_TRACKING_TASK_UUID,
    agent_id=AGENT_UUID,
    **shipment_tracking_task_def
)

def place_order(user_id, item_id, quantity):
    execution = client.executions.create(
        task_id=ORDER_PLACEMENT_TASK_UUID,
        input={
            "user_id": user_id,
            "order_details": {
                "item_id": item_id,
                "quantity": quantity
            }
        }
    )
    time.sleep(2)
    result = client.executions.get(execution.id)
    output = client.executions.transitions.list(execution_id=result.id).items[0].output

    if isinstance(output, dict):
        return output
    else:
        return {"order_id": output}

def check_inventory(item_id, quantity):
    execution = client.executions.create(
        task_id=INVENTORY_CHECK_TASK_UUID,
        input={
            "item_id": item_id,
            "quantity": quantity
        }
    )
    time.sleep(2)
    result = client.executions.get(execution.id)
    return client.executions.transitions.list(execution_id=result.id).items[0].output

def process_payment(user_id, order_id, amount):
    execution = client.executions.create(
        task_id=PAYMENT_PROCESSING_TASK_UUID,
        input={
            "user_id": user_id,
            "order_id": order_id,
            "amount": amount
        }
    )
    time.sleep(2)
    result = client.executions.get(execution.id)
    return client.executions.transitions.list(execution_id=result.id).items[0].output

def track_shipment(order_id):
    execution = client.executions.create(
        task_id=SHIPMENT_TRACKING_TASK_UUID,
        input={
            "order_id": order_id
        }
    )
    time.sleep(2)
    result = client.executions.get(execution.id)
    return client.executions.transitions.list(execution_id=result.id).items[0].output

print("Demonstrating E-commerce Order Processing Workflow:")

user_id = "user123"
item_id = 1
quantity = 2
amount = 49.99

is_available = check_inventory(item_id, quantity)
if is_available:
    print(f"Inventory Check: Item {item_id} is available.")
    order_result = place_order(user_id, item_id, quantity)
    print(f"Order Result: {order_result}")
    payment_result = process_payment(user_id, order_result["order_id"], amount)
    print(f"Payment Status: {payment_result}")
    shipment_result = track_shipment(order_result["order_id"])
    print(f"Shipment Status: {shipment_result}")
else:
    print(f"Inventory Check: Item {item_id} is not available.")

