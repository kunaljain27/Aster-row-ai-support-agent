# Orders Data Dictionary
The order snapshot contains customer-facing status fields plus internal customer, risk, and operational fields. The support agent must expose only sanitized customer-safe fields. `status` is authoritative. Delivery estimates are not valid for cancelled or returned orders, and a missing ETA must not be invented.
