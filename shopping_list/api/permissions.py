from rest_framework import permissions

from shopping_list.models import ShoppingList


class ShoppingListMembersOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.user.is_superuser:
            return True

        if request.user in obj.members.all():
            return True

        return False


class ShoppingItemShoppingListMembersOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.user.is_superuser:
            return True

        if request.user in obj.shopping_list.members.all():
            return True

        return False


class AllShoppingItemsShoppingListMembersOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        current_shopping_list = ShoppingList.objects.get(pk=view.kwargs.get("pk"))
        if request.user in current_shopping_list.members.all():
            return True

        return False
