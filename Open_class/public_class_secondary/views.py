from django.shortcuts import render
from django.http import HttpResponseRedirect
import datetime
import time
from .models import Design_table, Design_table_datail, Preparation_record, Observation_record, Growth_plan, Briefing_record
from .models import Secondary_Class as Class
from .random_code import randomString
from django.conf import settings

def create(request):
    if request.user.is_authenticated == False: # 未登入
        return HttpResponseRedirect('/account/login')
    if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
        return HttpResponseRedirect('/account/create')
    if request.user.teacher_department == '高中部': # 高中國中需分開
        return HttpResponseRedirect('class/high/create')
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
    if request.user.teacher_department == '高中部' :
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
    calendar_link = 'http://www.google.com/calendar/event?action=TEMPLATE&text=公開觀課（'
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
            'attend_link' : settings.HOST_NAME + '/class/secondary/attend/' + str(x.id) + '/' + x.attend_password,
            'attend_qr' : 'https://api.qrserver.com/v1/create-qr-code/?size=500x500&data=' + settings.HOST_NAME  + '/class/secondary/attend/' + str(x.id) + '/' + x.attend_password +'&format=png',
            'design' : '/class/secondary/design/' + str(x.id),
            'preparation' : '/class/secondary/preparation/' + str(x.id),
            'briefing' : '/class/secondary/briefing/' + str(x.id),
            'link' : calendar_link + x.teach_teacher + '）' + '&dates=' + datelink + startlink + '/' + datelink + endlink + '&details=' + request.user.teacher_department + x.subject + '公開觀課%0A授課老師：' + x.teach_teacher + '&location=' + x.class_room + '&trp=false'
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
            'link' : '/class/secondary/observation/' + str(x.id),
        })
    return render(request, 'class/myobservation.html',{ 'all_class' : all_class })

def design_table(request, no) :
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
    if Design_table.objects.filter(the_class = now_class).count() > 0 :
        return render(request, 'secondary/haddone.html')
    if 'dtid' in request.POST:
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'secondary/design_table.html', {
                'message': '未填寫完成',
                })
        try:
            now_table = Design_table(class_name = request.POST['class_name'], teach_teacher = request.user.teacher_name, teach_class = request.POST['teach_class'], 
                teaching_objectives = request.POST['teaching_objectives'], the_class = now_class)
            now_table.save()
            x, y= 'activity_1', 1 #動態表格部分
            while x in request.POST :
                Design_table_datail(teaching_activity = request.POST['activity_' + str(y)], teaching_aid = request.POST['aid_' + str(y)], 
                    assessment_method = request.POST['assessment_' + str(y)], teaching_method = request.POST['teaching_' + str(y)], 
                    time_allocation = request.POST['time_' + str(y)], the_design = now_table).save()
                x, y = 'activity_' + str(y + 1), y + 1
        except :
            return render(request, 'secondary/design_table.html', { 'message': '新增錯誤', })
        return render(request, 'secondary/success.html')
    return render(request, 'secondary/design_table.html')

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
        return render(request, 'secondary/haddone.html')
    if 'prid' in request.POST:
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'secondary/preparation_record.html', {
                'message': '未填寫完成',
                })
        try:
            start_time = datetime.datetime.strptime(request.POST['start_time'], '%H:%M')  # 轉時間格式
            end_time = datetime.datetime.strptime(request.POST['end_time'], '%H:%M')  # 轉時間格式
            if start_time >= end_time:  # 起始時間大於結束時間
                return render(request, 'secondary/preparation_record.html', {
                    'error_message': '時間錯誤',
                })
            Preparation_record(teach_date = request.POST['date'], teach_start_time = start_time, teach_end_time = end_time, teaching_grade = request.POST['teaching_grade'],
                class_name = request.POST['class_name'], teaching_sessions = request.POST['teaching_sessions'], source_of_teaching_material = request.POST['teaching_material'],
                content = request.POST['content'], teach_teacher = request.user.teacher_name, teaching_objectives = request.POST['teaching_objectives'],
                student_experience = request.POST['student_experience'], teaching_activity = request.POST['teaching_activity'], 
                evaluation_method = request.POST['evaluation_method'], the_class = now_class).save()
        except:
            return render(request, 'secondary/preparation_record.html', { 'message': '新增錯誤', })
        return render(request, 'secondary/success.html')
    return render(request, 'secondary/preparation_record.html')

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
        return render(request, 'secondary/haddone.html')
    if 'orid' in request.POST:
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'secondary/observation_record.html', {
                'message': '未填寫完成',
                })
        try:
            Observation_record(context = request.POST['context'], author = request.user.teacher_name, observation_date = request.POST['observation_date'],
                teach_teacher = request.POST['teach_teacher'], subject = request.POST['subject'], teach_class = request.POST['teach_class'], the_class = now_class,
                teaching_strategy_1 = request.POST['teaching_strategy_1'], teaching_strategy_1_text = request.POST['teaching_strategy_1_text'],
                teaching_strategy_2 = request.POST['teaching_strategy_2'], teaching_strategy_2_text = request.POST['teaching_strategy_2_text'],
                teaching_strategy_3 = request.POST['teaching_strategy_3'], teaching_strategy_3_text = request.POST['teaching_strategy_3_text'],
                teaching_strategy_4 = request.POST['teaching_strategy_4'], teaching_strategy_4_text = request.POST['teaching_strategy_4_text'],
                classroom_management_1 = request.POST['classroom_management_1'], classroom_management_1_text = request.POST['classroom_management_1_text'],
                classroom_management_2 = request.POST['classroom_management_2'], classroom_management_2_text = request.POST['classroom_management_2_text'],
                classroom_management_3 = request.POST['classroom_management_3'], classroom_management_3_text = request.POST['classroom_management_3_text'],
                classroom_management_4 = request.POST['classroom_management_4'], classroom_management_4_text = request.POST['classroom_management_4_text'],
                presenting_1 = request.POST['presenting_1'], presenting_1_text = request.POST['presenting_1_text'],
                presenting_2 = request.POST['presenting_2'], presenting_2_text = request.POST['presenting_2_text'],
                presenting_3 = request.POST['presenting_3'], presenting_3_text = request.POST['presenting_3_text'],
                presenting_4 = request.POST['presenting_4'], presenting_4_text = request.POST['presenting_4_text'],
                learning_environment_1 = request.POST['learning_environment_1'], learning_environment_1_text = request.POST['learning_environment_1_text'],
                learning_environment_2 = request.POST['learning_environment_2'], learning_environment_2_text = request.POST['learning_environment_2_text'],
                learning_environment_3 = request.POST['learning_environment_3'], learning_environment_3_text = request.POST['learning_environment_3_text'],
                learning_environment_4 = request.POST['learning_environment_4'], learning_environment_4_text = request.POST['learning_environment_4_text']).save()
            return render(request, 'secondary/success.html')
        except:
            return render(request, 'secondary/observation_record.html', { 'message': '新增錯誤', })
    return render(request, 'secondary/observation_record.html')

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
        return render(request, 'secondary/haddone.html')
    if 'brid' in request.POST:
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'secondary/briefing_record.html', {
                'message': '未填寫完成',
                })
        try:
            the_time = datetime.datetime.strptime(request.POST['briefing_time'], '%H:%M')
            now_record = Briefing_record(teach_teacher = request.user.teacher_name, observer = request.POST['observer'], briefing_date = request.POST['briefing_date'],
                briefing_time = the_time, advantages_and_features = request.POST['advantages_and_features'], adjust_or_change = request.POST['adjust_or_change'],
                learning_and_harvesting = request.POST['learning_and_harvesting'], the_class = now_class)
            now_record.save()
            x, y= 'growth_mode_1', 1 # 動態表格
            while x in request.POST :
                Growth_plan(growth_mode = request.POST['growth_mode_' + str(y)], abstract = request.POST['abstract_' + str(y)], member = request.POST['member_' + str(y)], 
                done_date = request.POST['done_date_' + str(y)], the_briefing = now_record).save()
                x, y = 'growth_mode_' + str(y + 1), y + 1
        except :
            return render(request, 'secondary/briefing_record.html', { 'message': '新增錯誤', })
        return render(request, 'secondary/success.html')
    return render(request, 'secondary/briefing_record.html')