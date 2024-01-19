from caisseApp.models import Product,AppUser,Code,Gift,Message,Facture,Category
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as loginUser
from django.views.decorators.csrf import csrf_exempt
import json
from django.core import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout as logoutUser



# is authentified----------------------------------------------------------------------------
def isAuth(request):
    if request.user.is_authenticated:
        return JsonResponse({'auth': True})
    else:
        return JsonResponse({'auth': False})

# register----------------------------------------------------------------------------
@csrf_exempt
def register(request):
    print("register called from app")
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # simple checks
        if not username or not email or not password:
            return JsonResponse({'status': 'error', 'message': 'Missing fields'})

        # simple checks
        if AppUser.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'Username already taken'})

        # create new user
        user = AppUser.objects.create(username=username, email=email, password=make_password(password))
        return JsonResponse({'status': 'success', 'message': 'User registered successfully'})

    return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'})

# login----------------------------------------------------------------------------
@csrf_exempt
def login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            loginUser(request, user)
            return JsonResponse({'status': 'success', 'message': 'Logged in successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}) 
    else: 
        return JsonResponse({'status': 'error', 'message': 'Only POST method allowed'})

        
# get the user info----------------------------------------------------------------------------
def getUserInfo(request):
    user = request.user
    user_json = serializers.serialize('json', [user, ])
    return JsonResponse({'user': user_json}) 



# logout ----------------------------------------------------------------------------

@csrf_exempt
def logout(request):
    logoutUser(request)
    return JsonResponse({'status': 'success', 'message': 'Logged out successfully'})


# create a code----------------------------------------------------------------------------
def createCode(request, gift_id, user_id):
    try:
        # Get gift and user objects
        gift = Gift.objects.get(pk=gift_id)
        user = AppUser.objects.get(pk=user_id)

        # Check if the user has enough points
        if user.points >= gift.pointCost:
            # na9ass the points from the user
            user.points -= gift.pointCost
            user.save()

            # Create a new code 
            code = Code.objects.create(giftId=gift, userId=user)

            # Return the id of the created code
            return JsonResponse({'status': 'success', 'code_id': code.pk})
        else:
            return JsonResponse({'status': 'error', 'message': 'Not enough points to redeem this gift.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# get user history----------------------------------------------------------------------------
def getUserHistory(request):
    try:
        user_id = request.user.id
        factures = Facture.objects.filter(userId=user_id).prefetch_related('transactionIds', 'transactionIds__productId')
        
        facture_data = []
        for facture in factures:
            transactions_data = []
            for transaction in facture.transactionIds.all():
                transaction_data = {
                    'productId': transaction.productId.id,
                    'productName': transaction.productId.name,
                    'productPrice': transaction.productId.price,
                    'productQuantity': transaction.quantity,
                    'productImage': transaction.productId.image.url,
                }
                transactions_data.append(transaction_data)
            
            facture_data.append({
                'factureId': facture.pk,
                'date': facture.date,
                'transactions': transactions_data,
            })
        
        return JsonResponse({'status': 'success', 'data': facture_data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# get user messages----------------------------------------------------------------------------
def getUserMessages(request):
    try:
        messages = Message.objects.all().order_by('-date')
        messages_data = [{
            'id': message.id,
            'fromUserId': message.fromUserId.id,
            'toUserId': message.toUserId.id,
            'fromUsername': 'FidelEase',
            'date': message.date.strftime('%Y-%m-%d %H:%M:%S'),
            'text': message.text,
        } for message in messages]

        return JsonResponse({'status': 'success', 'data': messages_data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

# get categorie----------------------------------------------------------------------------
def getCategories(request):
    try:
        categories = Category.objects.all()
        category_names = [category.name for category in categories]
        return JsonResponse({'status': 'success', 'categories': category_names})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# send a message----------------------------------------------------------------------------
@csrf_exempt
def sendMessage(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            from_user = request.user
            to_user = AppUser.objects.get(pk=1)
            text = data.get('text', None)

            Message.objects.create(fromUserId=from_user, toUserId=to_user, text=text)

            return JsonResponse({'status': 'success', 'message': 'Message sent successfully'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# get all products----------------------------------------------------------------------------
def products(request):
    products = Product.objects.select_related('category').all()
    
    # Create a custom list with category name
    products_data = []
    for product in products:
        product_data = {
            'pk': product.pk,
            'name': product.name,
            'price': product.price,
            'description': product.description,
            'category': product.category.name,  
            'image': str(product.image),
        }
        products_data.append(product_data)
    
    return JsonResponse({'status': 'success', 'data': products_data})

# Get all gifts----------------------------------------------------------------------------
def gifts(request):
    gifts = Gift.objects.all()
    gift_list = []
    for gift in gifts:
        product = gift.productId
        gift_data = {
            "id": gift.pk,
            "pointCost": gift.pointCost,
            "product": {
                "id": product.pk,
                "name": product.name,
                "price": product.price,
                "category": product.category.name,
                "description": product.description,
                "image": str(product.image),
            },
        }
        gift_list.append(gift_data)

    return JsonResponse({'status': 'success', 'data': gift_list})