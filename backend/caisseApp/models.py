from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
import secrets
import string

class AppUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        if not email:
            raise ValueError('Users must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class AppUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    points = models.PositiveIntegerField(default=0)
    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  # Add this for admin access
    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']  # Email & Password are required by default.

    objects = AppUserManager()

    def __str__(self):
        return self.username

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.FloatField(max_length=50)
    description = models.TextField(max_length=200)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    image=models.ImageField()
    
class Category(models.Model):
    name = models.CharField(max_length=50)
    
class Gift(models.Model):
    productId = models.ForeignKey("Product", on_delete=models.CASCADE)
    pointCost = models.IntegerField(max_length=50)

class Transaction(models.Model):
    productId=models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity=models.IntegerField(max_length=50)
    
class Message(models.Model):
    fromUserId=models.ForeignKey("AppUser", on_delete=models.CASCADE,related_name='fromWho')
    toUserId=models.ForeignKey("AppUser", on_delete=models.CASCADE,related_name='toWho')
    date=models.DateTimeField(auto_now_add=True)
    text=models.TextField()
    
class Code(models.Model):
    giftId = models.ForeignKey("Gift", on_delete=models.CASCADE)
    userId = models.ForeignKey("AppUser", on_delete=models.CASCADE)
    cid = models.CharField(primary_key=True, max_length=12, unique=True)

    def generate_unique_code(self):
        characters = string.ascii_letters
        while True:
            cid = ''.join(secrets.choice(characters) for _ in range(12))
            if not Code.objects.filter(cid=cid).exists():
                self.cid = cid
                break

    def save(self, *args, **kwargs):
        if not self.cid:
            self.generate_unique_code()
        super().save(*args, **kwargs)
    
class Facture(models.Model):
    transactionIds=models.ManyToManyField("Transaction")
    userId=models.ForeignKey("AppUser", on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)
    