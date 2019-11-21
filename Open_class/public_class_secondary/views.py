from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from .models import Design_table, Design_table_datail, Preparation_record, Observation_record, Growth_plan, Attend_data, Briefing_record, Secondary_Class as Class
from django.views import View
import datetime, time
from .random_code import randomString
from django.conf import settings
from public_class_high.models import High_Class
from public_class_high.models import Preparation_record as Hprep, Design_table as Hdesign

class create(View) :
    def get(self, request) :
        if request.user.is_authenticated == False: # 未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        if request.user.teacher_department == '高中部': # 高中國中需分開
            return HttpResponseRedirect('class/high/create')
        return render(request, 'class/create.html')
    def post(self, request) :
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'class/create.html', {'error_message': '未填寫完成'})
        try:
            start_time = datetime.datetime.strptime(request.POST['start_time'], '%H:%M')  # 轉時間格式
            end_time = datetime.datetime.strptime(request.POST['end_time'], '%H:%M')  # 轉時間格式
            if start_time >= end_time:  # 起始時間大於結束時間
                return render(request, 'class/create.html', {'error_message': '時間錯誤' })
            data = Attend_data(attend_password = randomString())
            data.save()
            Class(teach_teacher=request.user, subject=request.POST['subject'], class_room=request.POST['room'], 
                teach_date=request.POST['date'], teach_start_time=request.POST['start_time'], teach_end_time=request.POST['end_time'],
                attend_data = data, teaching_photo = '' ).save()  # 新增至database
        except:
            return render(request, 'class/create.html', { 'error_message': '新增錯誤', })
        return render(request, 'class/success.html')

class attend(View) :
    def get(self, request, no, password) :
        if request.user.is_authenticated == False: # 未登入
            return HttpResponseRedirect('/account/login?next=' + request.path)
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        try:
            the_class = Class.objects.get(pk = no) # 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        now = datetime.datetime.now().time()
        if datetime.date.today() != the_class.teach_date or now < the_class.teach_start_time or now > the_class.teach_end_time :
            return render(request, 'class/attend.html', { 'message': '非授課時間', })
        if request.user == the_class.teach_teacher :
            return render(request, 'class/attend.html', { 'message': '自己不用報到', })
        if request.user in the_class.attend_data.attend_people.all() : # 已參加
            return render(request, 'class/attend.html', { 'message': '已報到', })
        if password == the_class.attend_data.attend_password :
            the_class.attend_data.attend_number += 1
            the_class.attend_data.attend_people.add(request.user)
            the_class.attend_data.save()
            return render(request, 'class/attend.html', { 
                'message': '報到成功',
                'link' : '/class/secondary/observation/create/' + str(the_class.id),
            })
        else :
            return render(request, 'class/attend.html', { 'message': '密碼錯誤', })

class myclass(View) :
    calendar_link = 'http://www.google.com/calendar/event?action=TEMPLATE&text=公開授課（'
    def get(self, request) :
        if request.user.is_authenticated == False: # 未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        if request.user.teacher_department == '高中部' :
            return HttpResponseForbidden(content='您為高中部的')
        all_class = list()
        for x in list(Class.objects.filter(teach_teacher = request.user)) :
            datelink = str(x.teach_date).replace('-', '') + 'T' # 轉日期格式 YYYY-MM-DD to YYYYMMDD
            startlink, endlink  = str(x.teach_start_time).replace(':', ''), str(x.teach_end_time).replace(':', '') # 轉時間格式 HH:MM:SS to HHMMSS
            all_class.append({
                'subject' : x.subject,
                'date' : x.teach_date,
                'attend_number' : x.attend_data.attend_number,
                'attend_qr' : 'https://api.qrserver.com/v1/create-qr-code/?size=500x500&data=' + settings.HOST_NAME  + '/class/secondary/attend/' + str(x.id) + '/' + x.attend_data.attend_password +'&format=png',
                'design' : '/class/secondary/design/create/' + str(x.id),
                'preparation' : '/class/secondary/preparation/create/' + str(x.id),
                'briefing' : '/class/secondary/briefing/create/' + str(x.id),
                'observation' : '/class/secondary/observation/all/view/' + str(x.id),
                'link' : self.calendar_link + x.teach_teacher.teacher_name + '）' + '&dates=' + datelink + startlink + '/' + datelink + endlink + '&details=' + x.teach_teacher.teacher_department + x.subject + '公開授課%0A授課老師：' + x.teach_teacher.teacher_name + '&location=' + x.class_room + '&trp=false'
            })
            if x.teaching_photo !='':
                all_class[-1]['photo'] = x.teaching_photo
        return render(request, 'class/myclass.html',{ 'all_class' : all_class })

class myobservation(View) :
    def get(self, request) :
        if request.user.is_authenticated == False: # 未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        all_class = list()
        for x in list(Class.objects.all()) :
            if request.user not in x.attend_data.attend_people.all() : # 未參加
                continue
            all_class.append({
                'subject' : x.subject,
                'date' : x.teach_date,
                'observation' : '/class/secondary/observation/create/' + str(x.id),
            })
            if Design_table.objects.filter(the_class = x).count() > 0 :
                all_class[-1]['design'] = '/class/secondary/design/view/' + str(x.id)
            if Preparation_record.objects.filter(the_class = x).count() > 0 :
                all_class[-1]['preparation'] = '/class/secondary/preparation/view/' + str(x.id)
        for x in list(High_Class.objects.all()) :
            if request.user not in x.attend_data.attend_people.all() : # 未參加
                continue
            all_class.append({
                'subject' : x.subject,
                'date' : x.teach_date,
                'observation' : '/class/high/observation/create/' + str(x.id),
            })
            if Hdesign.objects.filter(the_class = x).count() > 0 :
                all_class[-1]['design'] = '/class/high/design/view/' + str(x.id)
            if Hprep.objects.filter(the_class = x).count() > 0 :
                all_class[-1]['preparation'] = '/class/high/preparation/view/' + str(x.id)
        return render(request, 'class/myobservation.html',{ 'all_class' : all_class })

class design_table_create(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        if now_class.teach_teacher != request.user : # 不是你的
            return HttpResponseForbidden(content='不是您的課')
        if Design_table.objects.filter(the_class = now_class).count() > 0 :
            return HttpResponseRedirect('/class/secondary/design/view/'+str(no))
        return render(request, 'secondary/design_table.html')
    def post(self, request, no) :
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        if now_class.teach_teacher != request.user : # 不是你的
            return HttpResponseForbidden(content='不是您的課')
        if Design_table.objects.filter(the_class = now_class).count() > 0 :
            return HttpResponseForbidden(content='已填寫')
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'secondary/design_table.html', { 'message': '未填寫完成' })
        try:
            now_table = Design_table(class_name = request.POST['class_name'], teach_teacher = request.user.teacher_name, teach_class = request.POST['teach_class'], 
                teaching_objectives = request.POST['teaching_objectives'], the_class = now_class)
            now_table.save()# 國中課程教學活動設計表
            x, y= 'activity_1', 1 #動態表格部分
            while x in request.POST :
                Design_table_datail(teaching_activity = request.POST['activity_' + str(y)], teaching_aid = request.POST['aid_' + str(y)], 
                    assessment_method = request.POST['assessment_' + str(y)], teaching_method = request.POST['teaching_' + str(y)], 
                    time_allocation = request.POST['time_' + str(y)], the_design = now_table).save()
                x, y = 'activity_' + str(y + 1), y + 1
        except :
            return render(request, 'secondary/design_table.html', { 'message': '新增錯誤', })
        return render(request, 'secondary/success.html')

class preparation_create(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        if now_class.teach_teacher != request.user : # 不是你的
            return HttpResponseForbidden(content='不是您的課')
        if Preparation_record.objects.filter(the_class = now_class).count() > 0 :
            return HttpResponseRedirect('/class/secondary/preparation/view/'+str(no))
        return render(request, 'secondary/preparation_record.html')
    def post(self, request, no) :
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        if now_class.teach_teacher != request.user : # 不是你的
            return HttpResponseForbidden(content='不是您的課')
        if Preparation_record.objects.filter(the_class = now_class).count() > 0 :
            return HttpResponseForbidden(content='已填寫')
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'secondary/preparation_record.html', { 'message': '未填寫完成' })
        try:
            start_time = datetime.datetime.strptime(request.POST['start_time'], '%H:%M')  # 轉時間格式
            end_time = datetime.datetime.strptime(request.POST['end_time'], '%H:%M')  # 轉時間格式
            if start_time >= end_time:  # 起始時間大於結束時間
                return render(request, 'secondary/preparation_record.html', { 'error_message': '時間錯誤' })
            Preparation_record(teach_date = request.POST['date'], teach_start_time = start_time, teach_end_time = end_time, teaching_grade = request.POST['teaching_grade'],
                class_name = request.POST['class_name'], teaching_sessions = request.POST['teaching_sessions'], source_of_teaching_material = request.POST['teaching_material'],
                content = request.POST['content'], teach_teacher = request.user.teacher_name, teaching_objectives = request.POST['teaching_objectives'],
                student_experience = request.POST['student_experience'], teaching_activity = request.POST['teaching_activity'], 
                evaluation_method = request.POST['evaluation_method'], the_class = now_class).save()
        except:
            return render(request, 'secondary/preparation_record.html', { 'message': '新增錯誤', })
        return render(request, 'secondary/success.html')

class observation_create(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        if request.user not in now_class.attend_data.attend_people.all() : # 未參加
            return HttpResponseForbidden(content='未參加')
        if Observation_record.objects.filter(the_class = now_class, author = request.user).count() > 0 :
            return HttpResponseRedirect('/class/secondary/observation/one/view/'+str(no))
        return render(request, 'secondary/observation_record.html')
    def post(self, request, no) :
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        if request.user not in now_class.attend_data.attend_people.all() : # 未參加
            return HttpResponseForbidden(content='未參加')
        if Observation_record.objects.filter(the_class = now_class, author = request.user).count() > 0 :
            return HttpResponseForbidden(content='已填寫')
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'secondary/observation_record.html', { 'message': '未填寫完成' })
        try:
            Observation_record(context = request.POST['context'], author = request.user, observation_date = request.POST['observation_date'],
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
        except:
            return render(request, 'secondary/observation_record.html', { 'message': '新增錯誤' })
        return render(request, 'secondary/success.html')

class briefing_create(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        if now_class.teach_teacher!= request.user : # 不是你的
            return HttpResponseForbidden(content='不是您的課')
        if Briefing_record.objects.filter(the_class = now_class).count() > 0 :
            return HttpResponseRedirect('/class/secondary/briefing/view/'+str(no))
        return render(request, 'secondary/briefing_record.html')
    def post(self, request, no) :
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        if now_class.teach_teacher!= request.user : # 不是你的
            return HttpResponseForbidden(content='不是您的課')
        if Briefing_record.objects.filter(the_class = now_class).count() > 0 :
            return HttpResponseForbidden(content='已填寫')
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'secondary/briefing_record.html', { 'message': '未填寫完成' })
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

class observation_all_view(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        people = list()
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        if now_class.teach_teacher!= request.user and request.user.power == False : # 沒權限
            return HttpResponseForbidden(content='沒權限')
        for x in now_class.attend_data.attend_people.all() :
            if Observation_record.objects.filter(the_class = now_class, author = x).count() > 0 :
                people.append({
                    'name' : x.teacher_name,
                    'link' : '/class/secondary/observation/one/view/' + str(Observation_record.objects.get(the_class = now_class, author = x).id)
                })
            else :
                people.append({
                    'name' : x.teacher_name,
                })
        return render(request, 'secondary/observation_record_all.html', { 'people' : people })

class observation_one_view(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        try:
            now_record = Observation_record.objects.get(pk = no)
        except :
            return HttpResponseNotFound(content='錯誤')
        if now_record.the_class.teach_teacher != request.user and now_record.author != request.user and request.user.power == False :  # 沒權限
            return HttpResponseForbidden(content='沒權限')
        return render(request, 'secondary/observation_record_detail.html',{
            'context' : now_record.context, 'author' : now_record.author, 'observation_date' : now_record.observation_date,
            'teach_teacher' : now_record.teach_teacher, 'subject' : now_record.subject, 'teach_class' : now_record.teach_class,
            'teaching_strategy_1' : now_record.teaching_strategy_1, 'teaching_strategy_1_text' : now_record.teaching_strategy_1_text,
            'teaching_strategy_2' : now_record.teaching_strategy_2, 'teaching_strategy_2_text' : now_record.teaching_strategy_2_text,
            'teaching_strategy_3' : now_record.teaching_strategy_3, 'teaching_strategy_3_text' : now_record.teaching_strategy_3_text,
            'teaching_strategy_4' : now_record.teaching_strategy_4, 'teaching_strategy_4_text' : now_record.teaching_strategy_4_text,
            'classroom_management_1' : now_record.classroom_management_1, 'classroom_management_1_text' : now_record.classroom_management_1_text,
            'classroom_management_2' : now_record.classroom_management_2, 'classroom_management_2_text' : now_record.classroom_management_2_text,
            'classroom_management_3' : now_record.classroom_management_3, 'classroom_management_3_text' : now_record.classroom_management_3_text,
            'classroom_management_4' : now_record.classroom_management_4, 'classroom_management_4_text' : now_record.classroom_management_4_text,
            'presenting_1' : now_record.presenting_1, 'presenting_1_text' : now_record.presenting_1_text,
            'presenting_2' : now_record.presenting_2, 'presenting_2_text' : now_record.presenting_2_text,
            'presenting_3' : now_record.presenting_3, 'presenting_3_text' : now_record.presenting_3_text,
            'presenting_4' : now_record.presenting_4, 'presenting_4_text' : now_record.presenting_4_text,
            'learning_environment_1' : now_record.learning_environment_1, 'learning_environment_1_text' : now_record.learning_environment_1_text,
            'learning_environment_2' : now_record.learning_environment_2, 'learning_environment_2_text' : now_record.learning_environment_2_text,
            'learning_environment_3' : now_record.learning_environment_3, 'learning_environment_3_text' : now_record.learning_environment_3_text,
            'learning_environment_4' : now_record.learning_environment_4, 'learning_environment_4_text' : now_record.learning_environment_4_text,
        })

class briefing_view(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        if now_class.teach_teacher != request.user and request.user.power == False : # 沒權限
            return HttpResponseForbidden(content='沒權限')
        if Briefing_record.objects.filter(the_class = now_class).count() > 0 : #取得議課紀錄表
            now_record = Briefing_record.objects.get(the_class = now_class)
        else :
            return HttpResponseNotFound(content='錯誤')
        return render(request, 'secondary/briefing_record_detail.html',{
                'observer' : now_record.observer,
                'teach_teacher' : now_record.teach_teacher,
                'briefing_date' : now_record.briefing_date,
                'briefing_time' : now_record.briefing_time, 
                'advantages_and_features' : now_record.advantages_and_features,
                'adjust_or_change' : now_record.adjust_or_change, 
                'learning_and_harvesting' : now_record.learning_and_harvesting,
                'detail' :  Growth_plan.objects.filter(the_briefing = now_record).all()
            })

class preparation_view(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        if Preparation_record.objects.filter(the_class = now_class).count() > 0 : #取得備課記錄表
            now_record = Preparation_record.objects.get(the_class = now_class)
        else :
            return HttpResponseNotFound(content='錯誤')
        if now_record.the_class.teach_teacher != request.user and request.user not in now_record.the_class.attend_data.attend_people.all() and request.user.power == False : # 沒權限
            return HttpResponseForbidden(content='沒權限')
        return render(request, 'secondary/preparation_record_detail.html',{
                'date' : now_record.teach_date, 'start_time' : now_record.teach_start_time, 'end_time' : now_record.teach_end_time,
                'teaching_grade' : now_record.teaching_grade, 'class_name' : now_record.class_name, 'teaching_sessions' : now_record.teaching_sessions,
                'teaching_material' : now_record.source_of_teaching_material, 'content' : now_record.content, 'teacher' : now_record.teach_teacher,
                'teaching_objectives' : now_record.teaching_objectives, 'student_experience' : now_record.student_experience,
                'teaching_activity' : now_record.teaching_activity, 'evaluation_method' : now_record.evaluation_method,
            })

class design_table_view(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        if Design_table.objects.filter(the_class = now_class).count() > 0 : #取得教學活動設計表
            now_table = Design_table.objects.get(the_class = now_class)
        else :
            return HttpResponseNotFound(content='錯誤')
        if now_table.the_class.teach_teacher != request.user and request.user not in now_table.the_class.attend_data.attend_people.all() and request.user.power == False : # 沒權限
            return HttpResponseForbidden(content='沒權限')
        return render(request, 'secondary/design_table_detail.html',{
                'class_name' : now_table.class_name, 'teacher' : now_table.class_name, 'teacher' : now_table.teach_teacher, 'teach_class' : now_table.teach_class,
                'teaching_objectives' : now_table.teaching_objectives, 'detail' : Design_table_datail.objects.filter(the_design = now_table).all()
            })

class admin(View):
    calendar_link = 'http://www.google.com/calendar/event?action=TEMPLATE&text=公開授課（'
    def get(self, request) :
        if request.user.is_authenticated == False: # 未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        if request.user.power == False : # 沒權限
            return HttpResponseForbidden(content='沒權限')
        all_class = list()
        if datetime.date.today().month >= 2 and datetime.date.today().month <= 7 :
            start_date, end_date = datetime.date(datetime.date.today().year, 2, 1), datetime.date(datetime.date.today().year, 7, 31)
        else :
            if datetime.date.today().month == 1 :
                start_date, end_date  = datetime.date(datetime.date.today().year - 1, 8, 1), datetime.date(datetime.date.today().year, 1, 31)
            else :
                start_date, end_date = datetime.date(datetime.date.today().year, 8, 1), datetime.date(datetime.date.today().year + 1, 1, 31)
        for x in list(Class.objects.filter(teach_date__range=(start_date, end_date))) :
            datelink = str(x.teach_date).replace('-', '') + 'T' # 轉日期格式 YYYY-MM-DD to YYYYMMDD
            startlink, endlink  = str(x.teach_start_time).replace(':', ''), str(x.teach_end_time).replace(':', '') # 轉時間格式 HH:MM:SS to HHMMSS
            all_class.append({
                'department' : x.teach_teacher.teacher_department,
                'teacher' : x.teach_teacher.teacher_name,
                'subject' : x.subject,
                'classroom' : x.class_room,
                'date' : x.teach_date,
                'start_time' : x.teach_start_time,
                'end_time' : x.teach_end_time,
                'attend_number' : x.attend_data.attend_number,
                'attend_qr' : 'https://api.qrserver.com/v1/create-qr-code/?size=500x500&data=' + settings.HOST_NAME  + '/class/secondary/attend/' + str(x.id) + '/' + x.attend_data.attend_password +'&format=png',
                'observation' : '/class/secondary/observation/all/view/' + str(x.id),
                'check' : '/class/secondary/check/' + str(x.id),
                'link' : self.calendar_link + x.teach_teacher.teacher_name + '）' + '&dates=' + datelink + startlink + '/' + datelink + endlink + '&details=' + x.teach_teacher.teacher_department + x.subject + '公開授課%0A授課老師：' + x.teach_teacher.teacher_name + '&location=' + x.class_room + '&trp=false'
            })
            if Design_table.objects.filter(the_class = x).count() > 0 :
                all_class[-1]['design'] = '/class/secondary/design/view/' + str(x.id)
            if Preparation_record.objects.filter(the_class = x).count() > 0 :
                all_class[-1]['preparation'] = '/class/secondary/preparation/view/' + str(x.id)
            if Briefing_record.objects.filter(the_class = x).count() > 0 :
                all_class[-1]['briefing'] = '/class/secondary/briefing/view/' + str(x.id)
        return render(request, 'class/admin.html',{ 'all_class' : all_class })

class check(View) :
    def get(self, request, no):
        if request.user.is_authenticated == False: # 未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        if request.user.power == False : # 沒權限
            return HttpResponseForbidden(content='沒權限')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        record, people = dict(), list()
        if Design_table.objects.filter(the_class = now_class).count() > 0 :
            record['design'] = '/class/secondary/design/view/' + str(no)
        if Preparation_record.objects.filter(the_class = now_class).count() > 0 :
            record['preparation'] = '/class/secondary/preparation/view/' + str(no)
        if Briefing_record.objects.filter(the_class = now_class).count() > 0 :
            record['briefing'] = '/class/secondary/briefing/view/' + str(no)
        for x in now_class.attend_data.attend_people.all() :
            if Observation_record.objects.filter(the_class = now_class, author = x).count() > 0 :
                people.append({
                    'name' : x.teacher_name,
                    'link' : '/class/secondary/observation/one/view/' + str(Observation_record.objects.get(the_class = now_class, author = x).id)
                })
            else :
                people.append({
                    'name' : x.teacher_name,
                })
        return render(request, 'class/check.html',{ 'class' : record, 'people' : people, 'link' : now_class.teaching_photo })
    def post(self, request, no) :
        if request.user.power == False : # 沒權限
            return HttpResponseForbidden(content='沒權限')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseNotFound(content='無此課')
        if request.POST['link'] == '' :
            return render(request, 'class/check.html', { 'message': '未填寫' })
        try:
            now_class.teaching_photo = request.POST['link']
            now_class.save()
        except :
            return render(request, 'class/check.html', { 'message': '錯誤' })
        return render(request, 'class/success.html')