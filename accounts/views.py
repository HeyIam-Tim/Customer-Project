from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users, admin_only


@login_required(login_url='login')
@admin_only
def home(request):
  customers = Customer.objects.all()
  orders = Order.objects.all()
  total_orders = orders.count()
  delivered = orders.filter(status='Delivered').count()
  pending = orders.filter(status='Pending').count()

  context = {'customers':
  customers, 'orders': orders, 'total_orders':total_orders, 'delivered':delivered, 'pending':pending}
  return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def products(request):
  products = Product.objects.all()
  context = {'products': products}
  return render(request, 'accounts/products.html', context)


@login_required(login_url='login')
def customer(request, customer_pk):
  customer = Customer.objects.get(id=customer_pk)
  orders = customer.order_set.all()
  total_orders = orders.count()
  myFilter = OrderFilter(request.GET, queryset=orders)
  orders = myFilter.qs
  context = {'customer':customer, 'orders':orders, 'total_orders':total_orders, 'myFilter':myFilter}
  return render(request, 'accounts/customer.html', context)


@login_required(login_url='login')
def createOrder(request, pk):
  OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)
  customer = Customer.objects.get(id=pk)
  formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
  #form = OrderForm(initial={'customer':customer})
  if request.method == 'POST':
    #form = OrderForm(request.POST)
    formset = OrderFormSet(request.POST, instance=customer)
    if formset.is_valid():
      customer = Customer.objects.get(id=pk).id
      formset.save()
      return redirect('customer', customer)
  context = {'formset':formset}
  return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
def updateOrder(request, pk_update):
  order = Order.objects.get(id=pk_update)
  form = OrderForm(instance=order)
  if request.method == 'POST':
    form = OrderForm(request.POST, instance=order)
    if form.is_valid():
      form.save()
      return redirect('/')
  context = {'form':form}
  return render(request, 'accounts/order_form.html', context)


@login_required(login_url='login')
def deleteOrder(request, pk):
  order = Order.objects.get(id=pk)
  if request.method == 'POST':
    customer_pk = order.customer.id
    order.delete()
    return redirect('customer', customer_pk)
  context = {'item':order}
  return render(request, 'accounts/delete.html', context)


@unauthenticated_user
def registerPage(request):
  form = CreateUserForm()
  if request.method == "POST":
    form = CreateUserForm(request.POST)
    if form.is_valid():
      user = form.save()
      username = form.cleaned_data.get('username')
      messages.success(request, 'Account was created for ' + username)

      return redirect('login')
  context = {'form':form}
  return render(request, 'accounts/register.html', context)


@unauthenticated_user
def loginPage(request):
  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(request, username=username, password=password)

    if user is not None:
      login(request, user)
      return redirect('home')
    else:
      messages.info(request, 'Username OR password is incorrect')
  context = {}
  return render(request, 'accounts/login.html', context)


def logout_user(request):
  logout(request)
  return redirect('login')


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
  orders = request.user.customer.order_set.all()
  total_orders = orders.count()
  delivered = orders.filter(status='Delivered').count()
  pending = orders.filter(status='Pending').count()
  context = {'orders':orders, 'total_orders':total_orders, 'delivered':delivered, 'pending':pending}
  return render(request, 'accounts/user.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
  customer = request.user.customer
  form = CustomerForm(instance=customer)

  if request.method == 'POST':
    form = CustomerForm(request.POST, request.FILES, instance=customer)

    if form.is_valid():
      form.save()

  context = {'form':form}
  return render(request, 'accounts/account_settings.html', context)