from django.urls import path

from .views import (
    sales_list, sale_list, sale_create, sale_detail, sale_to_job,
    sales_bank, api_sales_bank, house_interaction_create
)

urlpatterns = [
    # Daily sales entries (legacy)
    path("entries/", sales_list, name="sales_list"),
    
    # Individual sales/interactions
    path("sales/", sale_list, name="sale_list"),
    path("sale/new/", sale_create, name="sale_create"),
    path("sale/<int:house_id>/new/", sale_create, name="sale_create_for_house"),
    path("sale/<int:pk>/", sale_detail, name="sale_detail"),
    path("sale/<int:pk>/to-job/", sale_to_job, name="sale_to_job"),

    # Create a new house and optionally log interaction
    path("interaction/new/", house_interaction_create, name="house_interaction_create"),
    
    # Sales bank
    path("bank/", sales_bank, name="sales_bank"),
    path("api/bank/", api_sales_bank, name="api_sales_bank"),
]

