from django.db import models
from django.utils import timezone

# Create your models here.
class Contact(models.Model):
	name=models.CharField(max_length=50)
	email=models.EmailField()
	subject=models.CharField(max_length=100)
	message=models.TextField()

	def __str__(self):
		return self.name

class User(models.Model):
	username=models.CharField(max_length=100)
	email=models.EmailField()
	mobile=models.PositiveIntegerField()
	password=models.CharField(max_length=50)
	usertype=models.CharField(max_length=50,default="buyer")

	def __str__(self):
		return self.username

class Category(models.Model):
	name=models.CharField(max_length=200)

	def __str__(self):
		return self.name

class Brand(models.Model):
	name=models.CharField(max_length=200)

	def __str__(self):
		return self.name

class Color(models.Model):
	code=models.CharField(max_length=50)

	def __str__(self):
		return self.code

class Filter_Price(models.Model):
	FILTER_PRICE=(
		('1000_TO_10000','1000_TO_10000'),
		('10000_TO_20000','10000_TO_20000'),
		('20000_TO_30000','20000_TO_30000'),
		('30000_TO_40000','30000_TO_40000'),
		('40000_TO_50000','40000_TO_50000'),
	)

	price=models.CharField(choices=FILTER_PRICE,max_length=50)

	def __str__(self):
		return self.price

class Product(models.Model):
	CONDITION=(
		('new','new'),
		('old','old'),
	)

	STOCK=(
		('In_Stock','In_Stock'),
		('Out_Of_Stock','Out_Of_Stock'),
	)

	seller=models.ForeignKey(User,on_delete=models.CASCADE, related_name='seller_products')
	category=models.ForeignKey(Category,on_delete=models.CASCADE)
	brand=models.ForeignKey(Brand,on_delete=models.CASCADE)
	color=models.ForeignKey(Color,on_delete=models.CASCADE)
	filter_price=models.ForeignKey(Filter_Price,on_delete=models.CASCADE)
	name=models.CharField(max_length=200)
	price=models.IntegerField()
	m_image=models.ImageField(upload_to="product_image/")
	condition=models.CharField(choices=CONDITION,max_length=50)
	stock=models.CharField(choices=STOCK,max_length=50)
	info=models.TextField()
	desc=models.TextField()
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.name

class SliderImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="slider_images/")

    def __str__(self):
    	return self.product.name+"- Sub Image"

class Cart(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	product_price=models.PositiveIntegerField()
	product_qty=models.PositiveIntegerField()
	total_price=models.PositiveIntegerField()
	payment_status=models.BooleanField(default=False)

	def __str__(self):
		return self.user.username+" - "+self.product.name

class Wishlist(models.Model):
	user=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.user.username+" - "+self.product.name