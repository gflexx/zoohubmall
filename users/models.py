from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Don\'t forget your Email!')
        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password):
        user = self.create_user(
            email,
            full_name=full_name,
            password=password,
        )
        user.is_admin = True
        user.is_seller = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(max_length=162, unique=True)
    full_name = models.CharField(max_length=252)
    phone_number = models.CharField(max_length=11, blank=True)
    image = models.ImageField(upload_to='user_images/%Y/%m/%d', default='default.jpg')
    verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    joined = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    
    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def get_full_name(self):
        return self.full_name
       
    def get_name_from_mail(self):
    	mail = self.email
    	name = mail.strip('@')
    	return name[0]

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_verified(self):
        return self.verified

class CustomerAdmin(models.Manager):
    def get_or_new(self, request):
        user = request.user
        guest_id = request.session.get('guest_id')
        created = False
        customer_profile = None
        if user.is_authenticated:
            customer_profile, customer_profile_created = self.model.objects.get_or_create(user=user, email=user.email)
        elif guest_id is not None:
            guest = Guest.objects.get(id=guest_id)
            customer_profile, guest_profile_created = self.model.objects.get_or_create(email=guest.email)
        else:
            pass
        return customer_profile, created
        
class Customer(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    BY = 'is_buyer'
    SL = 'is_seller'
    CUSTOMER_TYPE = (
		(BY, 'I just want to buy stuff'),
		(SL, 'Buy and sell my products here'),
	)
    account_type = models.CharField(max_length=9, choices=CUSTOMER_TYPE, default=BY)
    profile_creation_complete = models.BooleanField(default=False)
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = CustomerAdmin()

    def __str__(self):
        return '{}'.format(self.email)
        
    def is_seller(self):
    	return self.account_type in (self.SL)

class Guest(models.Model):
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.email)

def customer_create(sender, instance, created, *args, **kwargs):
    if created and instance.email:
        Customer.objects.get_or_create(user=instance, email=instance.email)

def cusomer_profile(sender, instance, created, *args, **kwargs):
    if created:
        print('send to payment api')

post_save.connect(customer_create, sender=get_user_model())
