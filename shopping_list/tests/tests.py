from datetime import datetime, timedelta
from unittest import mock

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from shopping_list.models import ShoppingItem, ShoppingList, User


@pytest.mark.django_db
def test_valid_shopping_list_is_created(create_user, create_authenticated_client):

    user = create_user()
    client = create_authenticated_client(user)

    url = reverse("all-shopping-lists")

    data = {
        "name": "Groceries",
    }

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert ShoppingList.objects.get().name == "Groceries"


@pytest.mark.django_db
def test_shopping_list_name_missing_returns_bad_request(
    create_user, create_authenticated_client
):

    user = create_user()
    client = create_authenticated_client(user)

    url = reverse("all-shopping-lists")

    data = {
        "no_name": "no_groceries",
    }

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_all_shopping_lists_are_listed(
    create_user, create_authenticated_client, create_shopping_list
):

    user = create_user()
    client = create_authenticated_client(user)

    create_shopping_list("Groceries", user)
    create_shopping_list("Books", user)

    url = reverse("all-shopping-lists")
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    assert response.data["results"][0]["name"] == "Books"
    assert response.data["results"][1]["name"] == "Groceries"


@pytest.mark.django_db
def test_shopping_list_is_retrieved_by_id(
    create_user, create_authenticated_client, create_shopping_list
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)
    url = reverse("shopping-list-detail", args=[shopping_list.id])
    response = client.get(url, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Groceries"


@pytest.mark.django_db
def test_shopping_list_includes_only_corresponding_items(
    create_user, create_authenticated_client, create_shopping_list
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)
    another_shopping_list = create_shopping_list("Books", user)

    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Eggs", purchased=False
    )
    ShoppingItem.objects.create(
        shopping_list=another_shopping_list, name="The seven sisters", purchased=False
    )

    url = reverse("shopping-list-detail", args=[shopping_list.id])
    response = client.get(url)

    assert len(response.data["unpurchased_items"]) == 1
    assert response.data["unpurchased_items"][0]["name"] == "Eggs"


@pytest.mark.django_db
def test_shopping_list_name_is_changed(
    create_user, create_authenticated_client, create_shopping_list
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    data = {
        "name": "Food",
    }

    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Food"


@pytest.mark.django_db
def test_shopping_list_not_changed_because_name_missing(
    create_user, create_authenticated_client, create_shopping_list
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    data = {"something_else": "blahblah"}

    response = client.put(url, data=data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_shopping_list_name_is_changed_with_partial_update(
    create_user, create_authenticated_client, create_shopping_list
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    data = {
        "name": "Food",
    }

    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Food"


@pytest.mark.django_db
def test_partial_update_with_missing_name_has_no_impact(
    create_user, create_authenticated_client, create_shopping_list
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    data = {"something_else": "blahblah"}

    response = client.patch(url, data=data, format="json")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_shopping_list_is_deleted(
    create_user, create_authenticated_client, create_shopping_list
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(ShoppingList.objects.all()) == 0


@pytest.mark.django_db
def test_valid_shopping_item_is_created(
    create_user, create_authenticated_client, create_shopping_list
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    url = reverse("list-add-shopping-item", args=[shopping_list.id])

    data = {"name": "Milk", "purchased": False}

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_create_shopping_item_missing_data_returns_bad_request(
    create_user, create_authenticated_client, create_shopping_list
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    url = reverse("list-add-shopping-item", args=[shopping_list.id])

    data = {
        "name": "Milk",
    }

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_shopping_item_is_retrieved_by_id(
    create_user, create_authenticated_client, create_shopping_item
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse(
        "shopping-item-detail",
        kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id},
    )

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Chocolate"


@pytest.mark.django_db
def test_change_shopping_item_purchased_status(
    create_user, create_authenticated_client, create_shopping_item
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse(
        "shopping-item-detail",
        kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id},
    )

    data = {"name": "Chocolate", "purchased": True}
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingItem.objects.get().purchased is True


@pytest.mark.django_db
def test_change_shopping_item_purchased_status_with_missing_data_returns_bad_request(
    create_user, create_authenticated_client, create_shopping_item
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse(
        "shopping-item-detail",
        kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id},
    )

    data = {"purchased": True}
    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_change_shopping_item_purchased_status_with_partial_update(
    create_user, create_authenticated_client, create_shopping_item
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse(
        "shopping-item-detail",
        kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id},
    )

    data = {"purchased": True}
    response = client.patch(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingItem.objects.get().purchased is True


@pytest.mark.django_db
def test_shopping_item_is_deleted(
    create_user, create_authenticated_client, create_shopping_item
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse(
        "shopping-item-detail",
        kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id},
    )

    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(ShoppingItem.objects.all()) == 0


@pytest.mark.django_db
def test_shopping_list_is_deleted(
    create_user, create_authenticated_client, create_shopping_list
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(ShoppingList.objects.all()) == 0


@pytest.mark.django_db
def test_shopping_item_is_retrieved_by_id(
    create_user, create_authenticated_client, create_shopping_item
):

    user = create_user()
    client = create_authenticated_client(user)
    shopping_item = create_shopping_item(name="Chocolate", user=user)

    url = reverse(
        "shopping-item-detail",
        kwargs={"pk": shopping_item.shopping_list.id, "item_pk": shopping_item.id},
    )

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == "Chocolate"


@pytest.mark.django_db
def test_client_retrieves_only_shopping_lists_they_are_member_of(
    create_user, create_authenticated_client
):

    user = create_user()
    client = create_authenticated_client(user)

    shopping_list_1 = ShoppingList.objects.create(name="Groceries")
    shopping_list_1.members.add(user)

    another_user = User.objects.create_user(
        "SomeoneElse", "someone@else.com", "something"
    )
    shopping_list_2 = ShoppingList.objects.create(name="Books")
    shopping_list_2.members.add(another_user)

    url = reverse("all-shopping-lists")

    response = client.get(url)

    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == "Groceries"


@pytest.mark.django_db
def test_list_shopping_items_is_retrieved_by_shopping_list_member(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    shopping_list = create_shopping_list("Groceries", user)
    shopping_item_1 = ShoppingItem.objects.create(
        name="Oranges", purchased=False, shopping_list=shopping_list
    )
    shopping_item_2 = ShoppingItem.objects.create(
        name="Milk", purchased=False, shopping_list=shopping_list
    )

    client = create_authenticated_client(user)
    url = reverse("list-add-shopping-item", kwargs={"pk": shopping_list.id})
    response = client.get(url)

    assert len(response.data["results"]) == 2
    assert response.data["results"][0]["name"] == shopping_item_1.name
    assert response.data["results"][1]["name"] == shopping_item_2.name


@pytest.mark.django_db
def test_not_member_can_not_retrieve_shopping_items(
    create_user, create_authenticated_client, create_shopping_item
):
    shopping_list_creator = User.objects.create_user(
        "SomeoneElse", "someone@else.com", "something"
    )
    shopping_item = create_shopping_item("Milk", shopping_list_creator)

    user = create_user()
    client = create_authenticated_client(user)
    url = reverse(
        "list-add-shopping-item", kwargs={"pk": shopping_item.shopping_list.id}
    )

    response = client.get(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_shopping_items_only_the_ones_belonging_to_the_same_shopping_list(
    create_user, create_authenticated_client, create_shopping_list, create_shopping_item
):
    user = create_user()

    shopping_list = ShoppingList.objects.create(name="My shopping list")
    shopping_list.members.add(user)
    shopping_item_from_this_list = ShoppingItem.objects.create(
        name="Oranges", purchased=False, shopping_list=shopping_list
    )

    another_shopping_list = ShoppingList.objects.create(name="Another list")
    another_shopping_list.members.add(user)
    ShoppingItem.objects.create(
        name="Item from another list",
        purchased=False,
        shopping_list=another_shopping_list,
    )

    client = create_authenticated_client(user)
    url = reverse("list-add-shopping-item", kwargs={"pk": shopping_list.id})

    response = client.get(url)

    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == shopping_item_from_this_list.name


@pytest.mark.django_db
def test_max_3_shopping_items_on_shopping_list(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)

    shopping_list = create_shopping_list("Groceries", user)

    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Eggs", purchased=False
    )
    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Chocolate", purchased=False
    )
    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Milk", purchased=False
    )
    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Mango", purchased=False
    )

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    response = client.get(url, format="json")

    assert len(response.data["unpurchased_items"]) == 3


@pytest.mark.django_db
def test_all_shopping_items_on_shopping_list_unpurchased(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)

    shopping_list = create_shopping_list("Groceries", user)

    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Eggs", purchased=False
    )
    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Chocolate", purchased=True
    )
    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Milk", purchased=False
    )

    url = reverse("shopping-list-detail", args=[shopping_list.id])

    response = client.get(url, format="json")

    assert len(response.data["unpurchased_items"]) == 2


@pytest.mark.django_db
def test_duplicate_item_on_list_bad_request(
    create_user, create_authenticated_client, create_shopping_list
):

    user = create_user()
    client = create_authenticated_client(user)

    shopping_list = create_shopping_list("Groceries", user)
    ShoppingItem.objects.create(
        shopping_list=shopping_list, name="Milk", purchased=False
    )

    url = reverse("list-add-shopping-item", args=[shopping_list.id])

    data = {"name": "Milk", "purchased": False}

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert len(shopping_list.shopping_items.all()) == 1


@pytest.mark.django_db
def test_correct_order_shopping_lists(create_user, create_authenticated_client):
    url = reverse("all-shopping-lists")
    user = create_user()
    client = create_authenticated_client(user)

    old_time = datetime.now() - timedelta(days=1)
    older_time = datetime.now() - timedelta(days=100)

    with mock.patch("django.utils.timezone.now") as mock_now:
        mock_now.return_value = old_time
        ShoppingList.objects.create(name="Old").members.add(user)

        mock_now.return_value = older_time
        ShoppingList.objects.create(name="Oldest").members.add(user)

    ShoppingList.objects.create(name="New").members.add(user)

    response = client.get(url)

    assert response.data["results"][0]["name"] == "New"
    assert response.data["results"][1]["name"] == "Old"
    assert response.data["results"][2]["name"] == "Oldest"


@pytest.mark.django_db
def test_shopping_lists_order_changed_when_item_marked_purchased(
    create_user, create_authenticated_client
):

    user = create_user()
    client = create_authenticated_client(user)

    more_recent_time = datetime.now() - timedelta(days=1)
    older_time = datetime.now() - timedelta(days=20)

    with mock.patch("django.utils.timezone.now") as mock_now:
        mock_now.return_value = older_time
        older_list = ShoppingList.objects.create(name="Older")
        older_list.members.add(user)
        shopping_item_on_older_list = ShoppingItem.objects.create(
            name="Milk", purchased=False, shopping_list=older_list
        )

        mock_now.return_value = more_recent_time
        ShoppingList.objects.create(
            name="Recent", last_interaction=datetime.now() - timedelta(days=100)
        ).members.add(user)

    shopping_item_url = reverse(
        "shopping-item-detail",
        kwargs={"pk": older_list.id, "item_pk": shopping_item_on_older_list.id},
    )
    shopping_lists_url = reverse("all-shopping-lists")

    data = {"purchased": True}

    client.patch(shopping_item_url, data)

    response = client.get(shopping_lists_url)

    assert response.data["results"][1]["name"] == "Recent"
    assert response.data["results"][0]["name"] == "Older"


@pytest.mark.django_db
def test_call_with_token_authentication():
    username = "GirlThatLovesToCode"
    password = "something"
    User.objects.create_user(username, password=password)

    client = APIClient()
    token_url = reverse("api_token_auth")

    data = {"username": username, "password": password}

    token_response = client.post(token_url, data, format="json")
    token = token_response.data["token"]

    url = reverse("all-shopping-lists")
    client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_add_members_list_member(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    another_member = User.objects.create(username="another_member", password="whocares")
    third_member = User.objects.create(username="third_member", password="whocares")

    data = {"members": [another_member.id, third_member.id]}

    url = reverse("shopping-list-add-members", args=[shopping_list.id])

    response = client.put(url, data, format="json")

    assert len(response.data["members"]) == 3
    assert another_member.id in response.data["members"]
    assert third_member.id in response.data["members"]


@pytest.mark.django_db
def test_add_members_not_list_member(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)

    list_creator = User.objects.create(username="list_creator", password="whocares")
    shopping_list = create_shopping_list("Groceries", list_creator)

    data = {"members": [user.id]}

    url = reverse("shopping-list-add-members", args=[shopping_list.id])

    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_add_members_wrong_data(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    data = {"members": [11, 13]}

    url = reverse("shopping-list-add-members", args=[shopping_list.id])

    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_remove_members_list_member(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    another_member = User.objects.create(username="another_member", password="whocares")
    third_member = User.objects.create(username="third_member", password="whocares")

    shopping_list.members.add(another_member)
    shopping_list.members.add(third_member)

    data = {"members": [another_member.id, third_member.id]}

    url = reverse("shopping-list-remove-members", args=[shopping_list.id])
    response = client.put(url, data, format="json")

    assert len(response.data["members"]) == 1
    assert another_member.id not in response.data["members"]
    assert third_member.id not in response.data["members"]


@pytest.mark.django_db
def test_remove_members_not_list_member(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)

    list_creator = User.objects.create(username="list_creator", password="whocares")
    shopping_list = create_shopping_list("Groceries", list_creator)

    data = {"members": [user.id]}

    url = reverse("shopping-list-remove-members", args=[shopping_list.id])

    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_remove_members_wrong_data(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    data = {"members": [11, 13]}

    url = reverse("shopping-list-remove-members", args=[shopping_list.id])

    response = client.put(url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_search_returns_corresponding_shopping_item(
    create_user, create_authenticated_client, create_shopping_item
):
    user = create_user()
    client = create_authenticated_client(user)

    create_shopping_item("Chocolate", user)
    create_shopping_item("Skim milk", user)

    search_param = "?search=milk"
    url = reverse("search-shopping-items") + search_param

    response = client.get(url)

    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == "Skim milk"


@pytest.mark.django_db
def test_search_returns_only_users_results(
    create_user, create_authenticated_client, create_shopping_item
):
    user = create_user()
    client = create_authenticated_client(user)
    another_user = User.objects.create_user(
        "SomeOtherUser", "someother@user.com", "something"
    )

    create_shopping_item("Milk", user)
    create_shopping_item("Milk", another_user)

    search_param = "?search=milk"
    url = reverse("search-shopping-items") + search_param

    response = client.get(url)

    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_order_shopping_items_names_ascending(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    ShoppingItem.objects.create(
        name="Bananas", purchased=False, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Apples", purchased=False, shopping_list=shopping_list
    )

    order_param = "?ordering=name"
    url = reverse("list-add-shopping-item", args=[shopping_list.id]) + order_param

    response = client.get(url)

    assert response.data["results"][0]["name"] == "Apples"
    assert response.data["results"][1]["name"] == "Bananas"


@pytest.mark.django_db
def test_order_shopping_items_names_descending(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    ShoppingItem.objects.create(
        name="Apples", purchased=False, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Bananas", purchased=False, shopping_list=shopping_list
    )

    order_param = "?ordering=-name"
    url = reverse("list-add-shopping-item", args=[shopping_list.id]) + order_param

    response = client.get(url)

    assert response.data["results"][0]["name"] == "Bananas"
    assert response.data["results"][1]["name"] == "Apples"


@pytest.mark.django_db
def test_order_shopping_items_unpurchased_first(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    ShoppingItem.objects.create(
        name="Apples", purchased=False, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Bananas", purchased=True, shopping_list=shopping_list
    )

    order_param = "?ordering=purchased"
    url = reverse("list-add-shopping-item", args=[shopping_list.id]) + order_param

    response = client.get(url)

    assert response.data["results"][0]["name"] == "Apples"
    assert response.data["results"][1]["name"] == "Bananas"


@pytest.mark.django_db
def test_order_shopping_items_purchased_first(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    ShoppingItem.objects.create(
        name="Apples", purchased=False, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Bananas", purchased=True, shopping_list=shopping_list
    )

    order_param = "?ordering=-purchased"
    url = reverse("list-add-shopping-item", args=[shopping_list.id]) + order_param

    response = client.get(url)

    assert response.data["results"][0]["name"] == "Bananas"
    assert response.data["results"][1]["name"] == "Apples"


@pytest.mark.django_db
def test_order_shopping_items_purchased_and_names(
    create_user, create_authenticated_client, create_shopping_list
):
    user = create_user()
    client = create_authenticated_client(user)
    shopping_list = create_shopping_list("Groceries", user)

    ShoppingItem.objects.create(
        name="Apples", purchased=True, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Bananas", purchased=False, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Coconut", purchased=True, shopping_list=shopping_list
    )
    ShoppingItem.objects.create(
        name="Dates", purchased=False, shopping_list=shopping_list
    )

    order_param = "?ordering=purchased,name"
    url = reverse("list-add-shopping-item", args=[shopping_list.id]) + order_param

    response = client.get(url)

    assert response.data["results"][0]["name"] == "Bananas"
    assert response.data["results"][1]["name"] == "Dates"
    assert response.data["results"][2]["name"] == "Apples"
    assert response.data["results"][3]["name"] == "Coconut"
