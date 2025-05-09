from django.shortcuts import render, redirect
from .models import  order , Cart ,  Pet
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q 
import razorpay
import uuid
from django.core.mail import EmailMessage ,send_mail
from django.http import HttpResponse
 
# Create your views here.

def home(request):
    data = Pet.objects.all()
    request.session.pop('search_ids', None)
    return render(request, 'index.html', {'data': data})


def user_register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        username = request.POST['full_name'].strip()
        email = request.POST['email'].strip()
        password = request.POST['password'].strip()
        confirm_password = request.POST['confirm_password'].strip()

        if username == "" or email == "" or password == "" or confirm_password == "":
            error = 'All the fields are compulsory'
            return render(request, 'register.html', {'error': error})

        if password != confirm_password:
            return render(request, 'register.html', {'error': "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            error = 'Username already exists'
            return render(request, 'register.html', {'error': error})

        if User.objects.filter(email=email).exists():
            error = 'Email already exists'
            return render(request, 'register.html', {'error': error})

        user = User.objects.create(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()
        return redirect('login')


def getPetById(request, slug):
    pet = Pet.objects.get(slug=slug)
    return render(request, 'details.html', {'pet': pet})


def userLogin(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        u = request.POST['name']
        p = request.POST['password']
        user = authenticate(username=u, password=p)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            context = {'error': "Please enter valid credentials"}
            return render(request, 'login.html', context)


def userLogout(request):
    logout(request)
    return redirect('/')


def filterByCategory(request, catName):
    data = Pet.objects.filter(type=catName)
    return render(request, 'index.html', {'data': data})


def sortByPrice(request, direction):
    column = 'price'
    search_ids= request.session.get('search_ids')
    
    if direction == 'asc':
        column = 'price'
    else : 
        column = '-price'

    if search_ids:
        data = Pet.objects.filter(id__in=search_ids).order_by(column)
    else:
        data = Pet.objects.order_by(column)
    return render(request, 'index.html', {'data': data})


def filterByRange(request):
    min = request.GET['min_price']
    max = request.GET['max_price']
    search_ids = request.session.get('search_ids', None)

    if search_ids:
        data = Pet.objects.filter(id__in=search_ids, price__gte=min, price__lte=max)
    else:
        c1 = Q(price__gte=min)
        c2 = Q(price__lte=max)
        data = Pet.objects.filter(c1 & c2)

    return render(request, 'index.html', {'data': data})


def addToCart(request, petid):
    selectedPet = Pet.objects.get(id=petid)
    userid = request.user.id
    LoggedInUser = User.objects.get(id=userid)
    cart = Cart.objects.create(
        uid=LoggedInUser,
        petid=selectedPet
    )
    cart.save()
    return  redirect('/')


     


def searchPet(request):
    query = request.GET['query'].strip()

    if query == '':
        error = f'{query} No Search Result Found'
        print(error)
        return render(request, 'index.html', {'error': error})

    if Pet.objects.filter(Q(name__icontains=query)).exists():
        data = Pet.objects.filter(Q(name__icontains=query))
        request.session['search_ids'] = list(data.values_list('id', flat=True))
        return render(request, 'index.html', {'data': data})
    else:
        error = f'{query} No Result Found By Given Word'
        print(error)
        return render(request, 'index.html', {'error': error})
    


def showMyCart(request):
    userid = request.user.id 
    mycart = Cart.objects.filter(uid=userid)
    
    count = len(mycart)
    totalbill = sum(cart.petid.price * cart.quantity for cart in mycart)

    code = ''
    discount = 0
    error = ''

    if count >= 1:   
        if request.method == 'POST':
            if 'remove_coupon' in request.POST:
                code = ''
                discount = 0
                error = ''
            elif 'coupon_code' in request.POST:
                code = request.POST.get('coupon_code', '').strip().upper()

                COUPONS = {
                    'SAVE100': 100,
                    'FIRST50': 50,
                    'NEWUSER25': 25,
                    'SAVEPET':30,
                    'AMN':totalbill }

                if code in COUPONS:
                    discount = COUPONS[code]
                elif code:
                    error = '❌ NOT A VALID CODE'
    else:
        if request.method == 'POST':
            error = 'Please add at least one item to the cart to use a coupon.'
            

    final_bill = totalbill - discount
    request.session['final_bill'] = final_bill
    request.session['discount'] = discount
    request.session['code'] = code
    request.session['totalbill'] = totalbill


    return render(request, 'mycart.html', {
        'mycart': mycart,
        'count': count,
        'totalbill': totalbill,
        'discount': discount,
        'final_bill': final_bill,
        'code': code,
        'error': error,
    })


def removeCart(request ,cartid):
    mycart = Cart.objects.filter(id =cartid)
    mycart.delete()
    return redirect('/show-mycart')


def updateQuantity(request,cartid,operation):
    cart = Cart.objects.filter(id = cartid)
    for item in cart:
        print("Item ID:", item.id)
        
        print("Quantity:", item.quantity)
        
    if operation == 'incr':
        
        q=cart[0].quantity

        cart.update(quantity = q+1)
        return redirect('/show-mycart')
    
    if operation == 'decr':
        q=cart[0].quantity
        cart.update(quantity = q-1)
        return redirect('/show-mycart')


def confirmOrder(request):
    userid = request.user.id 
    mycart = Cart.objects.filter(uid=userid)
    final = Cart.objects.filter()
    
    count = len(mycart)
    

    finallbill = request.session.get('final_bill' ,None)
    discount = request.session.get('discount',None)
    totalbill = request.session.get('totalbill',None)
    code = request.session.get('code', None)

    request.session['final_bill'] = finallbill
    
    print(totalbill,discount,code,finallbill)
    return render(request,'confirm.html',{
        'mycart': mycart,
        'totalbill': totalbill,
        'discount':discount,
        'code':code,
        'count': count,
        'finallbill':finallbill,
        })

def contanct(request):
    return render(request, 'contanct.html')

def  makePayment(request):
    userid = request.user.id 
    data = Cart.objects.filter(uid = userid)
    amount = request.session.get('final_bill', None)
    totalbill = int(amount)
    
    client =razorpay.Client(auth=('rzp_test_6gcZVC7vhHuJQU','tkfCLSf4VW486pwqDKBtHbcp'))
    data ={
        'amount':totalbill * 100 ,
        'currency':'INR',
    }
    
    payment = client.order.create(data=data)
    print(payment)
    context ={}
    context['data'] = payment
    context['totalbill'] = totalbill
    return render(request,'pay.html', context )
     

def placeOrder(request):
    print("SESSION:", request.session.items())
    userid = request.user.id 
    ordid = uuid.uuid4()
    totalbill = request.session.get('final_bill',None)
    totalbill = request.session.get('final_bill') or request.GET.get('final_bill')
    
    if totalbill is None:
        return HttpResponse("Error: Total bill not found in session.")
    cartlist = Cart.objects.filter(uid = userid)
    for cart in cartlist:
       Order = order.objects.create(orderid = ordid , user_id = cart.uid , petid = cart.petid , quantity = cart.quantity, totalbill = totalbill)
       Order.save()
        

    cartlist.delete()
    
    sendmail(request, ordid)
    
    
    return redirect('/')


def sendmail(request,ordid):
    user = request.user
    msg = f"""
Hi {user.first_name or user.username},

Thank you for your order at PetStore! 🐾

Your order has been placed successfully. Here are the details:

Order ID: #{ordid}
Customer: {user.get_full_name() or user.username}
Email: {user.email}

We’ll notify you once your order is processed and on its way. If you have any questions, feel free to reply to this email.

Thank you for shopping with us!

Warm regards,  
PetStore Team 🐶🐱
"""

    send_mail(
        'Your PetStore Order Confirmation 🧾',
        msg,
        'mlucky1415@gmail.com',   
        [user.email ,'adityask080@gmail.com'],            
        fail_silently=False
    )

 