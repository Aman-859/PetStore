from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.
class Pet(models.Model):
    name= models.CharField(max_length=30)
    age = models.IntegerField()
    type = models.CharField(max_length=20)
    breed = models.CharField(max_length=20)
    price = models.IntegerField()
    slug =models.SlugField(unique=True ,blank= True)
    gender = models.CharField(max_length=6 , default='')
    description = models.CharField(max_length=200, default='')
    img = models.ImageField(upload_to='image',default='')

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=slugify(self.name)
        super().save(*args,**kwargs)

    
        

class Cart(models.Model):
    uid= models.ForeignKey(User, on_delete=models.CASCADE , db_column='uid')
    petid= models.ForeignKey(Pet, on_delete=models.CASCADE , db_column='petid')
    quantity=models.IntegerField(default=1)


class order(models.Model):
    orderid = models.CharField(max_length=50)
    user_id = models.ForeignKey(User, models.CASCADE,db_column='userid')
    petid = models.ForeignKey(Pet,on_delete=models.CASCADE,db_column='petid')
    quantity = models.IntegerField()
    totalbill = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)

    