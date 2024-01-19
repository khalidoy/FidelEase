from django.urls import path
from . import views

urlpatterns = [
path('login/', views.login, name = 'login'),
path('register/', views.register, name = 'register'),
path('isAuth/', views.isAuth, name = 'isAuth'),
path('logout/', views.logout, name = 'logout'),
path('products/', views.products, name = 'products'),
path('getUserInfo/', views.getUserInfo, name = 'getUserInfo'),
path('gifts/', views.gifts, name = 'gifts'),
path('createCode/<int:gift_id>/<int:user_id>/', views.createCode, name='createCode'),
path('getUserHistory/', views.getUserHistory, name = 'getUserHistory'),
path('getUserMessages/', views.getUserMessages, name = 'getUserMessages'),
path('sendMessage/', views.sendMessage, name = 'sendMessage'),
path('getCategories/', views.getCategories, name='getCategories'),

    
]


