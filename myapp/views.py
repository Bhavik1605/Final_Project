from django.shortcuts import render,redirect
from myapp. models import *
from django.conf import settings
from django.core.mail import send_mail
import random

from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import stripe

stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://localhost:8000'


def index(request):
	product=Product.objects.all()
	try:
		user=User.objects.get(email=request.session['email'])
		if user.usertype=="buyer":
			return render(request,'index.html',{'product':product})
		else:
			return redirect('seller-index') 
	except:
		return render(request,'index.html',{'product':product})


def seller_index(request):
	seller=User.objects.get(email=request.session['email'])
	product=Product.objects.filter(seller=seller)
	return render(request, 'seller-index.html',{'product':product})

def about(request):
	return render(request,'about.html')

def contact(request):
    if request.method=="POST":
        Contact.objects.create(
                name=request.POST['name'],
                email=request.POST['email'],
                subject=request.POST['subject'],
                message=request.POST['message']
            )
        msg="Contact Added Sucssesfully."
        return render(request,'contact.html',{'msg':msg})
    else:
        return render(request,'contact.html')

def register(request):
    if request.method=="POST":
        try:
            User.objects.get(email=request.POST['email'])
            msg="Email is Already Registered."
            return render(request,'login.html',{'msg':msg})
        except:
            if request.POST['password']==request.POST['cpassword']:
                User.objects.create(
                		usertype=request.POST['usertype'],
                        username=request.POST['username'],
                        email=request.POST['email'],
                        mobile=request.POST['mobile'],
                        password=request.POST['password']
                    )
                msg="Your Registration Sucssesfully Done."
                return render(request,'login.html',{'msg':msg})
            else:
                msg="Password & Confirm Password Does Not Matched"
                return render(request,'login.html',{'msg':msg})
    else:
        return render(request,'login.html')

def login(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            if user.password == request.POST['password']:
                if user.usertype == "buyer":
                    request.session['email'] = user.email
                    request.session['username'] = user.username
                    carts=Cart.objects.filter(user=user)
                    request.session['cart_count']=len(carts)
                    wishlists=Wishlist.objects.filter(user=user)
                    request.session['wishlist_count']=len(wishlists)
                    return redirect('index')
                else:
                    request.session['email'] = user.email
                    request.session['username'] = user.username
                    return redirect('seller-index')
            else:
                msg = "Password Is Incorrect"
                return render(request, 'login.html', {'msg': msg})
        except:
            msg = "Email Not Registered"
            return render(request, 'login.html', {'msg': msg})
    else:
        return render(request, 'login.html')


def logout(request):
    try:
        del request.session['email']
        del request.session['username']
        msg="User Logged Out Successfully"
        return render(request,'login.html',{'msg':msg})
    except:
        return render(request,'login.html')

def change_password(request):
    user = User.objects.get(email=request.session['email'])
    if request.method=="POST":
        if user.password==request.POST['old_password']:
            if request.POST['new_password']==request.POST['cnew_password']:
                user.password=request.POST['new_password']
                user.save()
                return redirect('logout')
            else:
                msg="New Password & Confirm New Password Does Not Matched"
                if user.usertype=="buyer":
                	return render(request,'change-password.html',{'msg':msg})
                else:
                	return render(request,'seller-change-password.html',{'msg':msg})
        else:
            msg="Old Password is Incoreect"
            if user.usertype=="buyer":
            	return render(request,'change-password.html',{'msg':msg})
            else:
            	return render(request,'seller-change-password.html',{'msg':msg})
    else:
        if user.usertype=="buyer":
        	return render(request,'change-password.html')
        else:
            return render(request,'seller-change-password.html')


def profile(request):
    user = User.objects.get(email=request.session['email'])
    if request.method == "POST":
        user.username = request.POST['username']
        user.mobile = request.POST['mobile']
        user.save()
        msg = "Profile Updated Successfully."
        if user.usertype == "buyer":
            return render(request, 'profile.html', {'user': user, 'msg': msg})
        else:
            return render(request, 'seller-profile.html', {'user': user, 'msg': msg})
    else:
        if user.usertype == "buyer":
            return render(request, 'profile.html', {'user': user})
        else:
            return render(request, 'seller-profile.html', {'user': user})

def forgot_password(request):
    if request.method=="POST":
        try:
            user=User.objects.get(email=request.POST['email'])
            otp=random.randint(10000,99999)
            subject = 'OTP for Forgot Password'
            message = 'Hello! '+user.username+', Your OTP for Forgot Password is : '+str(otp)
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail( subject, message, email_from, recipient_list )
            return render(request,'otp.html',{'email':user.email,'otp':otp})
        except:
            msg="Email Not Registered ."
            return render(request,'forgot-password.html',{'msg':msg})
    else:
        return render(request,'forgot-password.html')

def verify_otp(request):
    email=request.POST['email']
    otp=int(request.POST['otp'])
    uotp=int(request.POST['uotp'])

    if otp==uotp:
        return render(request,'new-password.html',{'email':email})
    else:
        msg="Invalid OTP"
        return render(request,'otp.html',{'email':email,'otp':otp,'msg':msg})

def new_password(request):
    email=request.POST['email']
    np=request.POST['new_password']
    cnp=request.POST['cnew_password']

    if np==cnp:
        user=User.objects.get(email=email)
        user.password=np
        user.save()
        msg="Your Password Updated Successfully."
        return render(request,'login.html',{'msg':msg})
    else:
        msg="New Password & Confirm New Password Does Not Matched."
        return render(request,'new-password.html',{'msg':msg,'email':email})

def add_product(request):
    seller = User.objects.get(email=request.session['email'])
    if request.method == 'POST':
        category_name = request.POST['category']
        brand_name = request.POST['brand']
        color_code = request.POST['code']
        filter_price=request.POST['filter_price']

        category, created = Category.objects.get_or_create(name=category_name)
        brand, created = Brand.objects.get_or_create(name=brand_name)
        color, created = Color.objects.get_or_create(code=color_code)
        price, created = Filter_Price.objects.get_or_create(price=filter_price)

        product = Product.objects.create(
            seller=seller,
            category=category,
            brand=brand,
            color=color,
            filter_price=price,
            name=request.POST['name'],
            price=request.POST['price'],
            condition=request.POST['condition'],
            stock=request.POST['stock'],
            info=request.POST['info'],
            desc=request.POST['desc'],
            m_image=request.FILES.get('image')
        )

        for i in range(1, 4):
            image_key = f'image{i}'
            if image_key in request.FILES:
                SliderImage.objects.create(product=product, image=request.FILES[image_key])

        msg = "Product Added Successfully"
        return render(request, 'add-product.html', {'msg': msg})
    else:
        return render(request, 'add-product.html')


def delete_product(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return redirect('seller-index')

def edit_product(request, pk):
    products = Product.objects.get(pk=pk)
    if request.method == 'POST':
        category = request.POST.get('category')
        filter_price = request.POST.get('filter_price')
        brand = request.POST.get('brand')
        condition = request.POST.get('condition')
        code = request.POST.get('code')
        stock = request.POST.get('stock')
        name = request.POST.get('name')
        price = request.POST.get('price')
        
        info = request.POST.get('info')
        desc = request.POST.get('desc')

        category, created = Category.objects.get_or_create(name=category)
        brand, created = Brand.objects.get_or_create(name=brand)
        color, created = Color.objects.get_or_create(code=code)
        filter_price, created = Filter_Price.objects.get_or_create(price=filter_price)

        products.category = category
        products.filter_price = filter_price
        products.brand = brand
        products.condition = condition
        products.color = color
        products.stock = stock
        products.name = name
        products.price = price
        products.info = info
        products.desc = desc
        try:
        	products.m_image = request.FILES['image']
        except:
        	pass

        products.save()

        for i in range(3):  # Assuming you have at most 3 slider images
            try:
                new = f'image{i+1}'
                new_image = request.FILES[new]
                old_slider_image = products.sliderimage_set.all()[i]
                old_slider_image.image = new_image
                old_slider_image.save()
            except:
            	pass

        msg = "Product Updated Successfully"
        return render(request, 'edit-product.html', {'msg': msg, 'products': products})
    else:
        return render(request, 'edit-product.html', {'products': products})

def seller_single_product(request, pk):
	single=Product.objects.get(pk=pk)
	return render(request, 'seller-single-product.html',{'single':single})

def shop(request):
	product=Product.objects.all()
	category=Category.objects.all()
	filter_price=Filter_Price.objects.all()
	color=Color.objects.all()
	brand=Brand.objects.all()

	category_id = request.GET.get('categories')
	price_id = request.GET.get('price')
	color_id = request.GET.get('color')
	brand_id = request.GET.get('brand')

	AtoZ_id = request.GET.get('AtoZ')
	ZtoA_id = request.GET.get('ZtoA')
	HtoL_id = request.GET.get('HtoL')
	LtoH_id = request.GET.get('LtoH')

	new_id = request.GET.get('new')
	old_id = request.GET.get('old')

	if category_id:
		product=Product.objects.filter(category=category_id)
	elif price_id:
		product=Product.objects.filter(filter_price=price_id)
	elif color_id:
		product=Product.objects.filter(color=color_id)
	elif brand_id:
		product=Product.objects.filter(brand=brand_id)
	elif AtoZ_id:
		product=Product.objects.all().order_by('name')
	elif ZtoA_id:
		product=Product.objects.all().order_by('-name')
	elif LtoH_id:
		product=Product.objects.all().order_by('price')
	elif HtoL_id:
		product=Product.objects.all().order_by('-price')
	elif HtoL_id:
		product=Product.objects.all().order_by('-price')
	elif new_id:
		product=Product.objects.filter(condition='new').order_by('-id')
	elif old_id:
		product=Product.objects.filter(condition='old').order_by('-id')
	else:
		product=Product.objects.all().order_by('-id') #last add show first

	return render(request,'shop.html',{'product':product,'category':category,'filter_price':filter_price,'color':color,'brand':brand})


def search(request):
	query=request.POST['query']

	if not query:
		msg="Please enter a search query"
		return render(request,'search.html',{'msg':msg})		

	product = Product.objects.filter(name__icontains = query)
	return render(request,'search.html',{'product':product})

def single_product(request,pk):
	cart_flag=False
	wishlist_flag=False
	single=Product.objects.get(pk=pk)
	user=User()
	try:
		user=User.objects.get(email=request.session['email'])
	except:
		return render(request,'login.html')
	try:
		Cart.objects.get(user=user,product=single)
		cart_flag=True
	except:
		pass
	try:
		Wishlist.objects.get(user=user,product=single)
		wishlist_flag=True
	except:
		pass
	return render(request,'single-product.html',{'single':single,'cart_flag':cart_flag,'wishlist_flag':wishlist_flag})


def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user)
	for i in carts:
		net_price+=i.total_price
	request.session['cart_count']=len(carts)
	return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	product_price=product.price
	product_qty=1
	Cart.objects.create(
		user=user,
		product=product,
		product_qty=product_qty,
		product_price=product_price,
		total_price=product_qty*product_price
	)
	return redirect('cart')

def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('cart')


def change_qty(request):
	pk=int(request.POST['count'])
	cart=Cart.objects.get(pk=pk)
	product_qty=int(request.POST['product_qty'])
	product_price=cart.product.price
	total_price=product_price*product_qty
	cart.product_qty=product_qty
	cart.total_price=total_price

	cart.save()
	return redirect('cart')

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(user=user,product=product)
	return redirect('wishlist')

def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'wishlist.html',{'wishlists':wishlists})

def remove_from_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	return redirect('wishlist')


@csrf_exempt
def create_checkout_session(request):
	amount = int(json.load(request)['post_data'])
	final_amount=amount*100
	session = stripe.checkout.Session.create(
		payment_method_types=['card'],
		line_items=[{
			'price_data': {
				'currency': 'inr',
				'product_data': {
					'name': 'Checkout Session Data',
					},
				'unit_amount': final_amount,
				},
			'quantity': 1,
			}],
		mode='payment',
		success_url=YOUR_DOMAIN + '/success.html',
		cancel_url=YOUR_DOMAIN + '/cancel.html',)
	return JsonResponse({'id': session.id})

def success(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=False)
	for i in carts:
		i.payment_status=True
		i.save()
	carts=Cart.objects.filter(user=user,payment_status=False)
	request.session['cart_count']=len(carts)
	return render(request,'success.html')

def cancel(request):
	return render(request,'cancel.html')

def myorder(request):
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,payment_status=True)
	return render(request,'myorder.html',{'carts':carts})
