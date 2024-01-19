from django.urls import path
from . import views

urlpatterns = [
path('login/', views.login,name='login'),
path('logout/', views.logout, name='logout'),
path('', views.products,name='products'),
path('productDetails/<int:id>', views.productDetails,name='productDetails'),
path('addProduct/', views.addProduct,name='addProduct'),
path('editProduct/<int:id>', views.editProduct,name='editProduct'),
path('deleteProduct/<int:id>', views.deleteProduct,name='deleteProduct'),
path('caisse/', views.caisse,name='caisse'),
path('facture/<int:id>', views.facture,name='facture'),
path('scanGiftCode/', views.scanGiftCode,name='scanGiftCode'),
path('gifts/', views.gifts,name='gifts'),
path('addGift/', views.addGift,name='addGift'),
path('editGift/<int:id>', views.editGift,name='editGift'),
path('deleteGift/<int:id>', views.deleteGift,name='deleteGift'),
path('history/', views.history,name='history'),
path('inbox/', views.inbox,name='inbox'),
path('sendMessage/<int:user_id>', views.sendMessage,name='sendMessage')

]





   


