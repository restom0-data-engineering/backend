"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from . import views
from . import analysis

urlpatterns = [
    path("customer/", views.fetch_customer_data, name="fetch_customer_data"),
    path("product/", views.fetch_product_data, name="fetch_product_data"),
    path("transaction/", views.fetch_transaction_data, name="fetch_transaction_data"),
    path(
        "click-stream/", views.fetch_click_stream_data, name="fetch_click_stream_data"
    ),
    path("customer-analysis/", analysis.customer_analysis, name="customer_analysis"),
    path(
        "transaction-analysis/",
        analysis.transaction_analysis,
        name="transaction_analysis",
    ),
    path("product-analysis/", analysis.product_analysis, name="product_analysis"),
    path(
        "behavioral-analysis/", analysis.behavioral_analysis, name="behavioral_analysis"
    ),
    path(
        "keyword-analysis/<int:month>/",
        analysis.keyword_analysis_bymonth,
        name="keyword_analysis_bymonth",
    ),
    path(
        "keyword-analysis/",
        analysis.keyword_analysis,
        name="keyword_analysis",
    ),
    path(
        "customer-segmentation/",
        analysis.customer_segmentation,
        name="customer_segmentation",
    ),
    path(
        "multiple-analysis/",
        analysis.multiple_analysis,
        name="multiple_analysis",
    ),
    path(
        "success-analysis/",
        analysis.get_product_sucessorder_percentage_analysis,
        name="get_product_sucessorder_percentage_analysis",
    ),
    path(
        "code-analysis/",
        analysis.get_code_analysis,
        name="get_code_analysis",
    ),
]
