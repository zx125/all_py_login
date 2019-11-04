from django.shortcuts import render,HttpResponse
from django.http import JsonResponse
from app01 import myforms
import random
from app01 import models
from  django.contrib import auth
from io import BytesIO,StringIO

# Create your views here.
def register(request):
    form_obj = myforms.MyRegForm()
    if request.method == 'POST':
        back_dic = {'code':1000,'msg':''}
        form_obj = myforms.MyRegForm(request.POST)

        #查看是否有错误
        if form_obj.is_valid():
            clean_data = form_obj.cleaned_data
            clean_data.pop('confirm_password')
            file_obj = request.FILES.get('avatar')
            if file_obj:
                clean_data['avatar'] = file_obj
            models.UserInfo.objects.create_user(**clean_data)
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)
    return render(request,'register.html',locals())

def login(request):
    if request.method == 'POST':
        back_dic = {'code':1000,'msg':''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        if request.session.get('code').upper() == code.upper():
            user_obj = auth.authenticate(username=username,password=password)
            if user_obj:
                auth.login(request,user_obj)
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 2000
                back_dic['msg'] = '用户名或者密码错误'
        else:
            back_dic['code'] = 3000
            back_dic['msg'] = '验证码错误'
        return JsonResponse(back_dic)
    return render(request,'login.html',locals())

def get_random():
    return random.randint(0,255),random.randint(0,255),random.randint(0,255)

from PIL import Image,ImageDraw,ImageFont

def get_code(request):
    img_obj = Image.new('RGB',(310,35),get_random())
    img_draw = ImageDraw.Draw(img_obj)
    img_font = ImageFont.truetype('static/font/111.ttf',30)

    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65,90))
        random_lower = chr(random.randint(97,122))
        random_int = str(random.randint(0,9))
        temp = random.choice([random_upper,random_lower,random_int])
        img_draw.text((i*45+45,0),temp,get_random(),img_font)
        code += temp
    print(code)

    request.session['code'] = code

    io_obj = BytesIO()
    img_obj.save(io_obj,'png')
    return HttpResponse(io_obj.getvalue())

def home(request):
    return render(request,'home.html')