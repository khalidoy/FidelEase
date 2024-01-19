from django.shortcuts import render,redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login as loginAuth
from django.contrib import messages
from .models import Product,AppUser,Code,Gift,Message,Transaction,Facture
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as logoutAuth
from .forms import ProductForm,GiftForm
from django.db.models import Q



def login(request):
    """
    Handle user login requests.

    GET requests render the login page. POST requests handle authentication.
    If authentication is successful, redirects to the 'products' page,
    otherwise, it redirects back to the login page with an error message.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    HttpResponse: The rendered login page for GET requests or a redirect for POST requests.
    """
    if(request.method=="GET"):
        return render(request, 'login.html')
    elif (request.method=="POST"):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            loginAuth(request, user)
            messages.success(request, 'Login successful.')
            return redirect('products') 
        else:
            messages.error(request, 'Invalid login credentials.')
            print("invalid credentials")
            return redirect('login')


def logout(request):
    """
    Log out the current user and redirect to the login page.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    HttpResponseRedirect: Redirects to the login page.
    """
    logoutAuth(request)
    return redirect('login') 


@login_required(login_url='login')
def products(request):
    """
    Display a list of all products.

    Requires the user to be logged in. Renders a page with all products.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    HttpResponse: The rendered products page.
    """
    allProducts = Product.objects.all()
    context={'product_list':allProducts}
    return render(request,'products.html',context)

@login_required(login_url='login')
def productDetails(request,id):
    """
    Display the details of a specific product.

    Requires the user to be logged in. Renders a page showing details
    of a product specified by its ID. If the product is not found, displays an error message.

    Parameters:
    request (HttpRequest): The HTTP request object.
    id (int): The ID of the product.

    Returns:
    HttpResponse: The rendered product details page or an error message.
    """
    p = Product.objects.get(pk=id)
    if p is not None:
        context={'product':p}
        return render(request,'productDetails.html',context)
    else : 
        messages.error("Product not found.")
   

@login_required(login_url='login')
def addProduct(request):
    """
    Add a new product to the database.

    Requires the user to be logged in. GET requests render a form for adding a new product.
    POST requests process the form data and add the product to the database.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    HttpResponse: The rendered form for GET requests or a redirect for POST requests.
    """
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('products')
    else:
        form = ProductForm()
    
    return render(request, 'addProduct.html', {'form': form})
        
    
@login_required(login_url='login')
def editProduct(request, id):
    """
    Edit an existing product.

    Requires the user to be logged in. GET requests render a form pre-filled with the product's
    existing data. POST requests update the product with the new data in the form.

    Parameters:
    request (HttpRequest): The HTTP request object.
    id (int): The ID of the product to edit.

    Returns:
    HttpResponse: The rendered edit form for GET requests or a redirect for POST requests.
    """
    product = Product.objects.get(pk=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products')  
    else:
        form = ProductForm(instance=product)

    return render(request, 'editProduct.html', {'form': form})



        
@login_required(login_url='login')
def deleteProduct(request,id):
    """
    Delete a specific product from the database.

    Requires the user to be logged in. GET requests render a confirmation page for product deletion.
    POST requests handle the actual deletion of the product.

    Parameters:
    request (HttpRequest): The HTTP request object.
    id (int): The ID of the product to be deleted.

    Returns:
    HttpResponse: The rendered confirmation page for GET requests or a redirect for POST requests.
    """
    if(request.method=="GET"):
        p = Product.objects.get(pk=id)
        context={"product":p}
        return render(request,'deleteProduct.html',context)
    elif(request.method=="POST"):
        if(Product.objects.get(pk=id).delete()):
            return redirect("products")
    else:
        messages.error(request,"Failed to delete the product.")
    
    
@login_required(login_url='login')
def caisse(request):
    """
    Handle the cash register functionality.

    Requires the user to be logged in. Displays all products and processes the transactions
    made at the cash register, including calculating total cost and points awarded.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    HttpResponse: The rendered cash register page or a redirect upon successful transaction.
    """
    products = Product.objects.all()  # Load all products to display in the form
    if request.method == "POST":
        userId = request.POST.get("userId")
        try:
            user = AppUser.objects.get(pk=userId)
        except AppUser.DoesNotExist:
            messages.error(request, 'AppUser does not exist!')
            return render(request, 'caisse.html', {'products': products})

        total = 0
        fac = Facture(userId=user)
        fac.save()  # Save early to generate an ID for ManyToMany relation

        # Process selected products
        for product in products:
            if str(product.id) in request.POST.getlist('products'):
                quantity = int(request.POST.get(f"quantity_{product.id}", 1))
                total += product.price * quantity
                transaction = Transaction(productId=product, quantity=quantity)
                transaction.save()
                fac.transactionIds.add(transaction)

        # Calculate and assign points
        points = total // 50  # Assuming integer division for points
        user.points += points
        user.save()

        return redirect("facture", fac.id)  # Redirect to a view that shows the facture

    return render(request, 'caisse.html', {'products': products})


            

@login_required(login_url='login')
def facture(request, id):
    """
    Display the details of a specific facture.

    Requires the user to be logged in. Retrieves and displays details of a facture specified by its ID.

    Parameters:
    request (HttpRequest): The HTTP request object.
    id (int): The ID of the facture.

    Returns:
    HttpResponse: The rendered facture details page.
    """
    facture = Facture.objects.get(pk=id)
    transactions = facture.transactionIds.all()
    total_cost = sum(t.productId.price * t.quantity for t in transactions)

    context = {
        'facture': facture,
        'transactions': transactions,
        'total_cost': total_cost,
    }
    return render(request, 'facture.html', context)
        


@login_required(login_url='login')
def scanGiftCode(request):
    """
    Handle the scanning of a gift code.

    Requires the user to be logged in. Allows the user to input a gift code and,
    if valid, displays the corresponding gift.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    HttpResponse: The rendered page for scanning gift codes.
    """
    gift = None
    if request.method == 'POST':
        gift_code = request.POST.get('giftCode')
        try:
            code = Code.objects.get(pk=gift_code)
            gift = code.giftId
        except Code.DoesNotExist:
            pass

    return render(request, 'scanGiftCode.html', {'gift': gift})
            
              
        
@login_required(login_url='login')
def gifts(request):
    """
    Display a list of all gifts.

    Requires the user to be logged in. Renders a page with all available gifts.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    HttpResponse: The rendered gifts page.
    """
    gifts = Gift.objects.all()
    return render(request, 'gifts.html', {'gifts': gifts})

    
    
@login_required(login_url='login')
def addGift(request):
    """
    Add a new gift to the database.

    Requires the user to be logged in. GET requests render a form for adding a new gift.
    POST requests process the form data and add the gift to the database.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    HttpResponse: The rendered form for GET requests or a redirect for POST requests.
    """
    if request.method == 'POST':
        form = GiftForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gifts')
    else:
        form = GiftForm()
    return render(request, 'addGift.html', {'form': form})


@login_required(login_url='login')
def editGift(request,id):
    """
    Edit an existing gift.

    Requires the user to be logged in. GET requests render a form pre-filled with the gift's
    existing data. POST requests update the gift with the new data in the form.

    Parameters:
    request (HttpRequest): The HTTP request object.
    id (int): The ID of the gift to edit.

    Returns:
    HttpResponse: The rendered edit form for GET requests or a redirect for POST requests.
    """
    gift = Gift.objects.get(pk=id)
    if request.method == 'POST':
        form = GiftForm(request.POST, instance=gift)
        if form.is_valid():
            form.save()
            return redirect('gifts')
    else:
        form = GiftForm(instance=gift)
        
    return render(request, 'editGift.html', {'form': form})

@login_required(login_url='login')        
def deleteGift(request,id):
    """
    Delete a specific gift from the database.

    Requires the user to be logged in. GET requests render a confirmation page for gift deletion.
    POST requests handle the actual deletion of the gift.

    Parameters:
    request (HttpRequest): The HTTP request object.
    id (int): The ID of the gift to be deleted.

    Returns:
    HttpResponse: The rendered confirmation page for GET requests or a redirect for POST requests.
    """
    if(request.method=="GET"):
        g = Gift.objects.get(pk=id)
        context={"gift":g}
        return render(request,'deleteGift.html',context)
    elif(request.method=="POST"):
        if(Gift.objects.get(pk=id).delete()):
            return redirect("gifts")
    else:
        messages.error(request,"Failed to delete the Gift.")

@login_required(login_url='login')
def history(request):
    """
    Display the transaction history.

    Requires the user to be logged in. Retrieves and displays a list of all factures,
    sorted by date.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    HttpResponse: The rendered transaction history page.
    """
    factures = Facture.objects.all().select_related('userId').order_by('-date')
    return render(request, 'history.html', {'factures': factures})
    

@login_required(login_url='login')
def inbox(request):
    """
    Display the inbox containing messages.

    Requires the user to be logged in. Retrieves and displays all messages ordered by date.

    Parameters:
    request (HttpRequest): The HTTP request object.

    Returns:
    HttpResponse: The rendered inbox page.
    """
    messages = Message.objects.all().order_by('-date').select_related('fromUserId', 'toUserId')
    return render(request, 'inbox.html', {'messages': messages})

@login_required(login_url='login')
def sendMessage(request, user_id):
    """
    Send a message to a specific user.

    Requires the user to be logged in. Handles the functionality to send a message from the
    logged-in user (admin) to another user specified by user_id.

    Parameters:
    request (HttpRequest): The HTTP request object.
    user_id (int): The ID of the user who will receive the message.

    Returns:
    HttpResponse: The rendered page for sending messages.
    """
    admin_id = request.user.id
    user = AppUser.objects.get(pk=user_id)
    # Fetch messages between the admin and the selected user
    messages = Message.objects.filter(
        (Q(fromUserId=admin_id) & Q(toUserId=user_id)) | 
        (Q(fromUserId=user_id) & Q(toUserId=admin_id))
    ).order_by('date')
    return render(request, 'sendMessage.html', {'messages': messages, 'user': user})
    