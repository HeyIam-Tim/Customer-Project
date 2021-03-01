from django.contrib import admin
from .models import *


class CustomerAdmin(admin.ModelAdmin):
  list_display = ('name', 'phone', 'email', 'date_created')


class ProductAdmin(admin.ModelAdmin):
  list_display = ('name', 'price')


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(Tag)