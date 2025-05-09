from django.contrib import admin
from .models import Pet,Cart ,order
# Register your models here.

class PetAdmin(admin.ModelAdmin):
    list_display = ['id', 'name' ,'age', 'type' ,'breed' ,'price','gender','description','img']
    list_filter =[ 'type' , 'price']


admin.site.register(Pet,PetAdmin)

class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'uid' ,'petid' ,'quantity' ]

admin.site.register(Cart , CartAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ['orderid' , 'user_id' , 'petid' , 'quantity' , 'totalbill']


admin.site.register(order, OrderAdmin)