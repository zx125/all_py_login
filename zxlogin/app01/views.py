from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse
from app01 import myforms
import random
from app01 import models
from  django.contrib import auth
from io import BytesIO,StringIO
from django.contrib.auth.decorators import login_required
import json
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

from utils.mypage import Pagination
def home(request):
    #获取所有的文章数据
    article_list = models.Article.objects.all()
    #使用分页器
    page_obj = Pagination(current_page=request.GET.get('page',1),all_count=article_list.count())
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request,'home.html',locals())

@login_required
def login_out(request):
    auth.logout(request)
    return redirect('/login/')

@login_required
def set_password(request):
    if request.is_ajax():
        back_dic = {'code':1000,'msg':''}
        if request.method == 'POST':
            username = request.POST.get('username')
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            #先校验两次密码是不是一致
            if new_password == confirm_password:
                #auth模块校验密码
                is_right = request.user.check_password(old_password)
                if is_right:
                    #设置新密码
                    request.user.set_password(new_password)
                    request.user.save()
                    back_dic['url'] = '/login/'
                else:
                    back_dic['code'] = 2000
                    back_dic['msg'] = '源密码错误'
            else:
                back_dic['code'] = 3000
                back_dic['msg'] = '两次密码不一致'
            return JsonResponse(back_dic)

def site(request,username,**kwargs):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        return render(request,'error.html')

    blog = user_obj.blog

    #获取此用户的文章
    article_list = models.Article.objects.filter(blog=blog)
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list =article_list.filter(tags=param)
        else:
            year,month = param.split('-')
            article_list = article_list.filter(create_time__year=year,create_time__month=month)

    #使用分页器
    page_obj = Pagination(current_page=request.GET.get('page',1),all_count=article_list.count())
    page_queryset = article_list[page_obj.start:page_obj.end]

    return render(request,'site.html',locals())

def article_detail(request,username,article_id):
    article_obj = models.Article.objects.filter(pk=article_id).first()
    comment_list = models.Comment.objects.filter(article=article_obj)
    return render(request,'article_detail.html',locals())

from django.db.models import F

def UpAndDown(request):
    print("sdasd")
    if request.is_ajax():
        if request.method == 'POST':
            back_dic = {'code':1000,'msg':''}
            #判断是否有用户登录，未登录不能点赞
            if request.user.is_authenticated():
                article_id = request.POST.get('article_id')
                is_up = request.POST.get('is_up')
                print(type(is_up))
                is_up = json.loads(is_up)

                article_obj = models.Article.objects.filter(pk=article_id).first()
                print(article_obj)

                #判断是不是当前用户的文章，自己不能给自己文章点赞
                if not article_obj.blog.userinfo == request.user:
                    #判断当前用户是否点过了
                    is_click = models.UpAndDown.objects.filter(user=request.user,article=article_obj)
                    if not is_click:
                        if is_up:
                            models.Article.objects.filter(pk=article_id).update(up_num = F('up_num')+1)
                            back_dic['msg'] = '点赞成功'
                        else:
                            models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                            back_dic['msg'] = '点踩成功'
                        models.UpAndDown.objects.create(user=request.user,article=article_obj,is_up=is_up)
                    else:
                        back_dic['code'] = 1001
                        back_dic['msg'] = '你已经点过了'
                else:
                    back_dic['code'] = 1002
                    back_dic['msg'] = '不能给自己的文章点赞'
            else:
                back_dic['code'] = 1003
                back_dic['msg'] = '请先<a href="/login/">登录</a>'
            return JsonResponse(back_dic)

from django.db import transaction
def comment(request):
    if request.is_ajax():
        if request.method == 'POST':
            back_dic = {'code':1000,'msg':''}
            article_id = request.POST.get('article_id')
            content = request.POST.get('content')
            parent_id = request.POST.get('parent_id')
            with transaction.atomic():
                models.Article.objects.filter(pk=article_id).update(comment_num = F('comment_num')+1)
                models.Comment.objects.create(user=request.user,article_id=article_id,content=content,parent_id=parent_id)
            back_dic['msg'] = '评论成功'
            return JsonResponse(back_dic)


