"""
URL configuration for petstore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
 
from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
path('',home),
path('login/', userLogin , name='login'),
path('register/', user_register ),
path('details/<slug:slug>' ,getPetById),
path('logout/',userLogout),
path('filter-by-cat/<catName>',filterByCategory),
path('sort-by-price/<direction>', sortByPrice),
path('filter-by-range/', filterByRange),
path('addcart/<petid>/' , addToCart),
path('search/', searchPet),
path('show-mycart/', showMyCart),
path('remove-cart/<cartid>', removeCart),
path('updatequantity/<cartid>/<operation>',updateQuantity ),
path('confirmorder/', confirmOrder),
path('contanct/', contanct),
path('makepayment/', makePayment),
path('placeoreder/', placeOrder),


 
]
urlpatterns += static (
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)