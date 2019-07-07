from django.shortcuts import render
from django.http import HttpResponseRedirect
import datetime
import time
from .models import Design_table, Design_table_datail, Preparation_record, Observation_record, Briefing_record
from .models import High_Class as Class
from .random_code import randomString

# Create your views here.

def create(request):
    if request.user.is_authenticated == False: # 未登入
        return HttpResponseRedirect('/account/login')
    if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
        return HttpResponseRedirect('/account/create')
    if request.user.teacher_department == '國中部': # 高中國中需分開
        return HttpResponseRedirect('class/secondary/create')
    if 'cid' in request.POST:
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'class/create.html', {'error_message': '未填寫完成'})
        try:
            start_time = datetime.datetime.strptime(request.POST['start_time'], '%H:%M')  # 轉時間格式
            end_time = datetime.datetime.strptime(request.POST['end_time'], '%H:%M')  # 轉時間格式
            if start_time >= end_time:  # 起始時間大於結束時間
                return render(request, 'class/create.html', {'error_message': '時間錯誤' })
            Class(teach_teacher=request.user.teacher_name, subject=request.POST['subject'], class_room=request.POST['room'], 
                teach_date=request.POST['date'], attend_password = randomString(), teach_start_time=request.POST['start_time'], 
                teach_end_time=request.POST['end_time'], teach_teacher_email = request.user.email ).save()  # 新增至database
        except:
            return render(request, 'class/create.html', { 'error_message': '新增錯誤', })
        return render(request, 'class/success.html')
    return render(request, 'class/create.html')

def attend(request, no, password) :
    if request.user.is_authenticated == False: # 未登入
        return HttpResponseRedirect('/account/login')
    if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
        return HttpResponseRedirect('/account/create')
    try:
        the_class = Class.objects.get(pk = no) # 取得課程
    except :
        return render(request, 'class/attend.html', { 'message': '無此課', })
    if request.user.teacher_department == '國中部' :
        return HttpResponseRedirect('/')
    now = datetime.datetime.now().time()
    if datetime.date.today() != the_class.teach_date or now < the_class.teach_start_time or now > the_class.teach_end_time :
        return render(request, 'class/attend.html', { 'message': '非授課時間', })
    if request.user.email == the_class.teach_teacher_email :
        return render(request, 'class/attend.html', { 'message': '自己不用報到', })
    if request.user in the_class.attend_people.all() : # 已參加
            return render(request, 'class/attend.html', { 'message': '已報到', })
    if password == the_class.attend_password :
        Class.objects.filter(id = no).update(attend_number = the_class.attend_number + 1)
        the_class.attend_people.add(request.user)
        return render(request, 'class/attend.html', { 'message': '報到成功', })
    else :
        return render(request, 'class/attend.html', { 'message': '密碼錯誤', })

def myclass(request) :
    if request.user.is_authenticated == False: # 未登入
        return HttpResponseRedirect('/account/login')
    if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
        return HttpResponseRedirect('/account/create')
    all_class = list()
    calendar_link = 'http://www.google.com/calendar/event?action=TEMPLATE&text=公開觀課'
    for x in list(Class.objects.all()) :
        if x.teach_teacher_email != request.user.email : # 不是自己的
            continue
        datelink = str(x.teach_date).replace('-', '') + 'T' # 轉日期格式 YYYY-MM-DD to YYYYMMDD
        startlink = str(x.teach_start_time).replace(':', '') # 轉時間格式 HH:MM:SS to HHMMSS
        endlink = str(x.teach_end_time).replace(':', '') # 轉時間格式 HH:MM:SS to HHMMSS
        all_class.append({
            'subject' : x.subject,
            'date' : x.teach_date,
            'attend_number' : x.attend_number,
            'attend_link' : 'localhost:8000/class/high/attend/' + str(x.id) + '/' + x.attend_password,
            'attend_qr' : 'https://api.qrserver.com/v1/create-qr-code/?size=500x500&data=localhost:8000/class/high/attend/' + str(x.id) + '/' + x.attend_password +'&format=png',
            'design' : '/class/high/design/' + str(x.id),
            'preparation' : '/class/high/preparation/' + str(x.id),
            'briefing' : '/class/high/briefing/' + str(x.id),
            'link' : calendar_link + '&dates=' + datelink + startlink + '/' + datelink + endlink + '&details=' + request.user.teacher_department + x.subject + '公開觀課%0A授課老師：' + x.teach_teacher + '&location=' + x.class_room + '&trp=false'
        })
    return render(request, 'class/myclass.html',{ 'all_class' : all_class })

def myobservation(request) :
    if request.user.is_authenticated == False: # 未登入
        return HttpResponseRedirect('/account/login')
    if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
        return HttpResponseRedirect('/account/create')
    all_class = list()
    for x in list(Class.objects.all()) :
        if request.user not in x.attend_people.all() : # 未參加
            continue
        all_class.append({
            'subject' : x.subject,
            'date' : x.teach_date,
            'link' : '/class/high/observation/' + str(x.id),
        })
    return render(request, 'class/myobservation.html',{ 'all_class' : all_class })

def design_table(request, no) :
    if request.user.is_authenticated == False:  #未登入
        return HttpResponseRedirect('/account/login')
    if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
        return HttpResponseRedirect('/')
    try:
        now_class = Class.objects.get(pk = no)# 取得高中課程教學活動設計表
        if now_class.teach_teacher_email != request.user.email :
            return render(request, 'high/design_table.html', { 'message': '錯誤', })
    except :
        return render(request, 'high/design_table.html', { 'message': '錯誤', })
    if Design_table.objects.filter(the_class = now_class).count() > 0 :
        return render(request, 'high/haddone.html')
    if 'dtid' in request.POST:
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'high/design_table.html', {
                'message': '未填寫完成',
                })
        x, y= 'teaching_objectives_1', 1 #動態表格部分
        try:
            start_time = datetime.datetime.strptime(request.POST['start_time'], '%H:%M')  # 轉時間格式
            end_time = datetime.datetime.strptime(request.POST['end_time'], '%H:%M')  # 轉時間格式
            if start_time >= end_time:  # 起始時間大於結束時間
                return render(request, 'class/design_table.html', {'message': '時間錯誤' })
            now_table = Design_table(class_name = request.POST['class_name'], teach_teacher = request.user.teacher_name, teach_class = request.POST['teach_class'],
                source_of_teaching_material = request.POST['teaching_material'], teach_date = request.POST['date'], teach_start_time = request.POST['start_time'],
                teach_end_time = request.POST['end_time'], background_analysis = request.POST['background_analysis'], teaching_method = request.POST['big_teaching_method'],
                teaching_resources = request.POST['teaching_resources'], reference_material = request.POST['reference_material'],
                teaching_objectives = request.POST['big_teaching_objectives'], the_class = now_class)
            now_table.save()
            x, y= 'teaching_objectives_1', 1 #動態表格部分
            while x in request.POST :
                Design_table_datail(teaching_objectives = request.POST['teaching_objectives_' + str(y)], teacher_activity = request.POST['teacher_activity_' + str(y)], 
                    student_activities = request.POST['student_activities_' + str(y)], teaching_aid = request.POST['teaching_aid_' + str(y)], 
                    assessment_method = request.POST['assessment_method_' + str(y)], teaching_method = request.POST['teaching_method_' + str(y)],
                    time_allocation = request.POST['time_allocation_' + str(y)], the_design = now_table).save()
                x, y = 'teaching_objectives_' + str(y + 1), y + 1
        except :
            return render(request, 'high/design_table.html', { 'message': '新增錯誤', })
        return render(request, 'high/success.html')
    return render(request, 'high/design_table.html')

def preparation(request, no) :
    if request.user.is_authenticated == False:  #未登入
        return HttpResponseRedirect('/account/login')
    if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
        return HttpResponseRedirect('/')
    try:
        now_class = Class.objects.get(pk = no)# 取得課程
        if now_class.teach_teacher_email != request.user.email : # 不是你的
            return HttpResponseRedirect('/')
    except :
        return HttpResponseRedirect('/')
    if Preparation_record.objects.filter(the_class = now_class).count() > 0 :
        return render(request, 'high/haddone.html')
    if 'prid' in request.POST:
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'high/preparation_record.html', {
                'message': '未填寫完成',
                })
        try:
            start_time = datetime.datetime.strptime(request.POST['start_time'], '%H:%M')  # 轉時間格式
            end_time = datetime.datetime.strptime(request.POST['end_time'], '%H:%M')  # 轉時間格式
            if start_time >= end_time:  # 起始時間大於結束時間
                return render(request, 'high/preparation_record.html', {
                    'error_message': '時間錯誤',
                })
            Preparation_record(subject = request.POST['subject'], author = request.user.teacher_name, teach_date = request.POST['date'], teach_start_time = start_time, 
                teach_end_time = end_time, teaching_grade = request.POST['teaching_grade'], class_name = request.POST['class_name'], 
                teach_teacher = request.user.teacher_name, source_of_teaching_material = request.POST['teaching_material'],
                content = request.POST['content'], teaching_objectives = request.POST['teaching_objectives'],
                student_experience = request.POST['student_experience'], teaching_activity = request.POST['teaching_activity'], 
                evaluation_method = request.POST['evaluation_method'], the_class = now_class).save()
        except:
            return render(request, 'high/preparation_record.html', { 'message': '新增錯誤', })
        return render(request, 'high/success.html')
    return render(request, 'high/preparation_record.html')

def observation(request, no) :
    if request.user.is_authenticated == False:  #未登入
        return HttpResponseRedirect('/account/login')
    if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
        return HttpResponseRedirect('/')
    try:
        now_class = Class.objects.get(pk = no)# 取得課程
        if request.user not in now_class.attend_people.all() : # 未參加
            return HttpResponseRedirect('/')
    except :
        return HttpResponseRedirect('/')
    if Observation_record.objects.filter(the_class = now_class, author = request.user.teacher_name).count() > 0 :
        return render(request, 'high/haddone.html')
    if 'orid' in request.POST:
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'high/observation_record.html', {
                'message': '未填寫完成',
                })
        try:
            Observation_record(author = request.user.teacher_name, observation_date = request.POST['observation_date'], teach_teacher = request.POST['teach_teacher'], 
                subject = request.POST['subject'], class_name = request.POST['class_name'], learning_atmosphere = request.POST['learning_atmosphere'],
                learning_process = request.POST['learning_process'], learning_result = request.POST['learning_result'], 
                experience_and_learning = request.POST['experience_and_learning'], the_class = now_class).save()
            return render(request, 'high/success.html')
        except:
            return render(request, 'high/observation_record.html', { 'message': '新增錯誤', })
    return render(request, 'high/observation_record.html')

def briefing(request, no) :
    if request.user.is_authenticated == False:  #未登入
        return HttpResponseRedirect('/account/login')
    if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
        return HttpResponseRedirect('/')
    try:
        now_class = Class.objects.get(pk = no)# 取得課程
        if now_class.teach_teacher_email != request.user.email : # 不是你的
            return HttpResponseRedirect('/')
    except :
        return HttpResponseRedirect('/')
    if Briefing_record.objects.filter(the_class = now_class).count() > 0 :
        return render(request, 'high/haddone.html')
    if 'brid' in request.POST:
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'high/briefing_record.html', {
                'message': '未填寫完成',
                })
        try:
            the_time = datetime.datetime.strptime(request.POST['briefing_time'], '%H:%M')
            now_record = Briefing_record(teach_teacher = request.user.teacher_name, observer = request.POST['observer'], briefing_date = request.POST['briefing_date'],
                briefing_time = the_time, affirmation_teaching_performance = request.POST['affirmation_teaching_performance'], 
                guide_discussion_teaching_performance = request.POST['guide_discussion_teaching_performance'], judgment_performance = request.POST['judgment_performance'], 
                suggest = request.POST['suggest'], growth_activity = request.POST['growth_activity'], the_class = now_class).save()
        except :
            return render(request, 'high/briefing_record.html', { 'message': '新增錯誤', })
        return render(request, 'high/success.html')
    return render(request, 'high/briefing_record.html')