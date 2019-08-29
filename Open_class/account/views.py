from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from .models import User

# Create your views here.
def login(request) :
    return render(request, 'account/login.html')

class Create(View) :
    subject_choice = ['國文科', '英文科', '數學科', '社會科', '自然科', '其他科']
    department_choice = ['高中部', '國中部']
    def get(self, request) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name != '' and request.user.teacher_subject != '' and request.user.teacher_department != '': # 已註冊
            return HttpResponseRedirect('/')
        return render(request , 'account/create.html',{
            'email' : request.user.email,
            'subject_choice' : self.subject_choice,
            'department_choice' : self.department_choice
        })
    def post(self, request) :
        if request.user.teacher_name != '' and request.user.teacher_subject != '' and request.user.teacher_department != '': # 已註冊
            return HttpResponseBadRequest(content='重複註冊')
        if request.POST['subject'] =='' or request.POST['name'] == '' or request.POST['department'] =='': # 未輸入完成
            return render(request , 'account/create.html' , {
                'error_message' : '未輸入完成',
                'email' : request.user.email,
                'subject_choice' : subject_choice,
                'department_choice' : department_choice
            })
        if request.POST['subject'] not in self.subject_choice or request.POST['department'] not in self.department_choice :# 沒有此選項
            return render(request , 'account/create.html' , {
                'error_message' : '你以為我不會檢查嗎?',
                'email' : request.user.email,
                'subject_choice' : self.subject_choice,
                'department_choice' : self.department_choice
            })
        User.objects.filter(email = request.user.email).update(teacher_subject = request.POST['subject'], teacher_name = request.POST['name'], 
            teacher_department = request.POST['department'], power = False)
        return HttpResponseRedirect('/')


