from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import User

# Create your views here.
def login(request) :
    return render(request, 'account/login.html')

def create(request) :
    if request.user.is_authenticated == False:  #未登入
        return HttpResponseRedirect('/account/login')
    if request.user.teacher_name != '' and request.user.teacher_subject != '' and request.user.teacher_department != '': # 已註冊
        return HttpResponseRedirect('/')
    subject_choice = ['國文科', '英文科', '數學科', '社會科', '自然科', '藝體輔']
    department_choice = ['高中部', '國中部']
    if 'rid' in request.POST:
        if request.POST['subject'] =='' or request.POST['name'] == '' or request.POST['department'] =='': # 未輸入完成
            return render(request , 'account/create.html' , {
                'error_message' : '未輸入完成',
                'email' : request.user.email,
                'subject_choice' : subject_choice,
                'department_choice' : department_choice
            })
        if request.POST['subject'] not in subject_choice or request.POST['department'] not in department_choice :# 沒有此選項
            return render(request , 'account/create.html' , {
                'error_message' : '你以為我不會檢查嗎?',
                'email' : request.user.email,
                'subject_choice' : subject_choice,
                'department_choice' : department_choice
            })
        User.objects.filter(email = request.user.email).update(teacher_subject = request.POST['subject'], teacher_name = request.POST['name'], teacher_department = request.POST['department'])
        return HttpResponseRedirect('/')
    return render(request , 'account/create.html',{
        'email' : request.user.email,
        'subject_choice' : subject_choice,
        'department_choice' : department_choice
    })

