from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_func):
  def wrapper_func2(request, *args, **kwargs):
    
    if request.user.is_authenticated:
      return redirect('home')
    else:
      return view_func(request, *args, **kwargs)

  return wrapper_func2


def allowed_users(allowed_roles=[]):
  def decorator(view_func):
    def wrapper_func1(request, *args, **kwargs):
      
      group = None
      if request.user.groups.exists():
        group = request.user.groups.all()[0].name

      if group in allowed_roles:
        return view_func(request, *args, **kwargs)

      else:
        return HttpResponse('You are not authorized to view this page.')

    return wrapper_func1

  return decorator


def admin_only(view_func):
  def wrapper_func3(request, *args, **kwargs):
    group = None
    if request.user.groups.exists():
      group = request.user.groups.all()[0].name

    if group == 'customer':
      return redirect("user-page")

    if group == 'admin':
      return view_func(request, *args, **kwargs)

  return wrapper_func3