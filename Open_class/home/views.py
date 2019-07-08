from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import auth
from account.models import User
from public_class_secondary.models import Secondary_Class as SClass
from public_class_high.models import High_Class as HClass
import datetime

def home(request):
    if request.user.is_authenticated == False: # 未登入
        return HttpResponseRedirect('/account/login')
    if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
        return HttpResponseRedirect('/account/create')
    all_class = list()
    calendar_link = 'http://www.google.com/calendar/event?action=TEMPLATE&text=公開觀課（'
    Class = HClass
    if request.user.teacher_department == '國中部':
        Class = SClass
    for x in list(Class.objects.all()) :
        if x.teach_date < datetime.date.today() :
            continue
        datelink = str(x.teach_date).replace('-', '') + 'T' # 轉日期格式 YYYY-MM-DD to YYYYMMDD
        startlink = str(x.teach_start_time).replace(':', '') # 轉時間格式 HH:MM:SS to HHMMSS
        endlink = str(x.teach_end_time).replace(':', '') # 轉時間格式 HH:MM:SS to HHMMSS
        department = User.objects.get(email = x.teach_teacher_email).teacher_department # 部門
        all_class.append({
            'department' : department,
            'teacher' : x.teach_teacher,
            'subject' : x.subject,
            'classroom' : x.class_room,
            'date' : x.teach_date,
            'start_time' : x.teach_start_time,
            'end_time' : x.teach_end_time,
            'link' : calendar_link + x.teach_teacher + '）' + '&dates=' + datelink + startlink + '/' + datelink + endlink + '&details=' + department + x.subject + '公開觀課%0A授課老師：' + x.teach_teacher + '&location=' + x.class_room + '&trp=false'
        })
    return render(request, 'home/home.html',{ 'all_class' : all_class })

