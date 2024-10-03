from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from shopping_list.models import ShoppingItem, ShoppingList, User

admin.site.register(ShoppingItem)
admin.site.register(ShoppingList)

admin.site.register(User, UserAdmin)
