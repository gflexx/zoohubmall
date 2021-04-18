from django.dispatch import Signal

purchased_product_signal = Signal(providing_args=['instance', 'request'])
