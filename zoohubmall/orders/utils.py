import random
import string

def random_string_generator(size=12, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
    
def generate_order_id(instance):
    new_order_id = random_string_generator().upper()
    Klass = instance.__class__
    qs_exists = Klass.objects.filter(order_id=new_order_id).exists()
    if qs_exists:
        return generate_order_id(instance)
    return new_order_id
    