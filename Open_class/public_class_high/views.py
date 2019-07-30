from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
import datetime, time
from .models import Design_table, Design_table_datail, Preparation_record, Observation_record, Briefing_record, Attend_data, High_Class as Class
from .random_code import randomString
from django.conf import settings

class create(View) :
    def get(self, request) :
        if request.user.is_authenticated == False: # 未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        if request.user.teacher_department == '國中部': # 高中國中需分開
            return HttpResponseRedirect('class/secondary/create')
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
                teach_date=request.POST['date'], teach_start_time=request.POST['start_time'], 
                teach_end_time=request.POST['end_time'], attend_data = data, teaching_photo = '').save()  # 新增至database
        except:
            return render(request, 'class/create.html', { 'error_message': '新增錯誤', })
        return render(request, 'class/success.html')

class attend(View) :
    def get(self, request, no, password) :
        if request.user.is_authenticated == False: # 未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        if request.user.teacher_department == '國中部' :
            return HttpResponseRedirect('/')
        try:
            the_class = Class.objects.get(pk = no) # 取得課程
        except :
            return render(request, 'class/attend.html', { 'message': '無此課', })
        now = datetime.datetime.now().time()
        if datetime.date.today() != the_class.teach_date or now < the_class.teach_start_time or now > the_class.teach_end_time :
            return render(request, 'class/attend.html', { 'message': '非授課時間', })
        if request.user == the_class.teach_teacher :
            return render(request, 'class/attend.html', { 'message': '自己不用報到', })
        if request.user in the_class.attend_data.attend_people.all() : # 已參加
            return render(request, 'class/attend.html', { 'message': '已報到', })
        if password == the_class.attend_data.attend_password :
            the_class.attend_data.attend_number += 1
            the_class.attend_data.save()
            the_class.attend_data.attend_people.add(request.user)
            return render(request, 'class/attend.html', { 'message': '報到成功', })
        else :
            return render(request, 'class/attend.html', { 'message': '密碼錯誤', })

class myclass(View) :
    calendar_link = 'http://www.google.com/calendar/event?action=TEMPLATE&text=公開授課（'
    def get(self, request) :
        if request.user.is_authenticated == False: # 未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        if request.user.teacher_department == '國中部' :
            return HttpResponseRedirect('/')
        all_class = list()
        for x in list(Class.objects.all()) :
            if x.teach_teacher != request.user : # 不是自己的
                continue
            datelink = str(x.teach_date).replace('-', '') + 'T' # 轉日期格式 YYYY-MM-DD to YYYYMMDD
            startlink, endlink  = str(x.teach_start_time).replace(':', ''), str(x.teach_end_time).replace(':', '') # 轉時間格式 HH:MM:SS to HHMMSS
            all_class.append({
                'subject' : x.subject,
                'date' : x.teach_date,
                'attend_number' : x.attend_data.attend_number,
                'attend_qr' : 'https://api.qrserver.com/v1/create-qr-code/?size=500x500&data=' + settings.HOST_NAME  + '/class/high/attend/' + str(x.id) + '/' + x.attend_data.attend_password +'&format=png',
                'design' : '/class/high/design/create/' + str(x.id),
                'preparation' : '/class/high/preparation/create/' + str(x.id),
                'briefing' : '/class/high/briefing/create/' + str(x.id),
                'observation' : '/class/high/observation/all/view/' + str(x.id),
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
                'observation' : '/class/high/observation/create/' + str(x.id),
            })
            if Design_table.objects.filter(the_class = x).count() > 0 :
                all_class[-1]['design'] = '/class/high/design/view/' + str(x.id)
            if Preparation_record.objects.filter(the_class = x).count() > 0 :
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
            return HttpResponseRedirect('/')
        if now_class.teach_teacher != request.user : # 不是你的
            return HttpResponseRedirect('/')
        if Design_table.objects.filter(the_class = now_class).count() > 0 :
            return HttpResponseRedirect('/class/high/design/view/'+str(no))
        return render(request, 'high/design_table.html')
    def post(self, request, no) :
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'high/design_table.html', { 'message': '未填寫完成' })
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
            start_time = datetime.datetime.strptime(request.POST['start_time'], '%H:%M')  # 轉時間格式
            end_time = datetime.datetime.strptime(request.POST['end_time'], '%H:%M')  # 轉時間格式
            if start_time >= end_time:  # 起始時間大於結束時間
                return render(request, 'class/design_table.html', {'message': '時間錯誤' })
            now_table = Design_table(class_name = request.POST['class_name'], teach_teacher = request.user.teacher_name, teach_class = request.POST['teach_class'],
                source_of_teaching_material = request.POST['teaching_material'], teach_date = request.POST['date'], teach_start_time = request.POST['start_time'],
                teach_end_time = request.POST['end_time'], background_analysis = request.POST['background_analysis'], teaching_method = request.POST['big_teaching_method'],
                teaching_resources = request.POST['teaching_resources'], reference_material = request.POST['reference_material'],
                teaching_objectives = request.POST['big_teaching_objectives'], the_class = now_class)
            now_table.save() # 高中課程教學活動設計表
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

class preparation_create(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseRedirect('/')
        if now_class.teach_teacher != request.user : # 不是你的
                return HttpResponseRedirect('/')
        if Preparation_record.objects.filter(the_class = now_class).count() > 0 :
            return HttpResponseRedirect('/class/high/preparation/view/'+str(no))
        return render(request, 'high/preparation_record.html')
    def post(self, request, no) :
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'high/preparation_record.html', { 'message': '未填寫完成' })
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
            start_time = datetime.datetime.strptime(request.POST['start_time'], '%H:%M')  # 轉時間格式
            end_time = datetime.datetime.strptime(request.POST['end_time'], '%H:%M')  # 轉時間格式
            if start_time >= end_time:  # 起始時間大於結束時間
                return render(request, 'high/preparation_record.html', { 'error_message': '時間錯誤' })
            Preparation_record(subject = request.POST['subject'], author = request.user.teacher_name, teach_date = request.POST['date'], teach_start_time = start_time, 
                teach_end_time = end_time, teaching_grade = request.POST['teaching_grade'], class_name = request.POST['class_name'], 
                teach_teacher = request.user.teacher_name, source_of_teaching_material = request.POST['teaching_material'],
                content = request.POST['content'], teaching_objectives = request.POST['teaching_objectives'],
                student_experience = request.POST['student_experience'], teaching_activity = request.POST['teaching_activity'], 
                evaluation_method = request.POST['evaluation_method'], the_class = now_class).save()
        except:
            return render(request, 'high/preparation_record.html', { 'message': '新增錯誤', })
        return render(request, 'high/success.html')

class observation_create(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseRedirect('/')
        if request.user not in now_class.attend_data.attend_people.all() : # 未參加
            return HttpResponseRedirect('/')
        if Observation_record.objects.filter(the_class = now_class, author = request.user).count() > 0 :
            return HttpResponseRedirect('/class/high/observation/one/view/'+str(no))
        return render(request, 'high/observation_record.html')
    def post(self, request, no) :
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'high/observation_record.html', { 'message': '未填寫完成' })
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
            Observation_record(author = request.user, observation_date = request.POST['observation_date'], teach_teacher = request.POST['teach_teacher'], 
                subject = request.POST['subject'], class_name = request.POST['class_name'], learning_atmosphere = request.POST['learning_atmosphere'],
                learning_process = request.POST['learning_process'], learning_result = request.POST['learning_result'], 
                experience_and_learning = request.POST['experience_and_learning'], the_class = now_class).save()
        except:
            return render(request, 'high/observation_record.html', { 'message': '新增錯誤' })
        return render(request, 'high/success.html')

class briefing_create(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseRedirect('/')
        if now_class.teach_teacher!= request.user : # 不是你的
            return HttpResponseRedirect('/')
        if Briefing_record.objects.filter(the_class = now_class).count() > 0 :
            return HttpResponseRedirect('/class/high/briefing/view/'+str(no))
        return render(request, 'high/briefing_record.html')
    def post(self, request, no) :
        for x in request.POST:  # 有空
            if x == '':
                return render(request, 'high/briefing_record.html', { 'message': '未填寫完成' })
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
            the_time = datetime.datetime.strptime(request.POST['briefing_time'], '%H:%M')
            now_record = Briefing_record(teach_teacher = request.user.teacher_name, observer = request.POST['observer'], briefing_date = request.POST['briefing_date'],
                briefing_time = the_time, affirmation_teaching_performance = request.POST['affirmation_teaching_performance'], 
                guide_discussion_teaching_performance = request.POST['guide_discussion_teaching_performance'], judgment_performance = request.POST['judgment_performance'], 
                suggest = request.POST['suggest'], growth_activity = request.POST['growth_activity'], the_class = now_class).save()
        except :
            return render(request, 'high/briefing_record.html', { 'message': '新增錯誤', })
        return render(request, 'high/success.html')

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
            return render(request, 'high/observation_record_all.html', { 'message': '錯誤' })
        if now_class.teach_teacher!= request.user and request.user.power == False : # 沒權限
            return HttpResponseRedirect('/')
        for x in now_class.attend_data.attend_people.all() :
            if Observation_record.objects.filter(the_class = now_class, author = x).count() > 0 :
                people.append({
                    'name' : x.teacher_name,
                    'link' : '/class/high/observation/one/view/' + str(Observation_record.objects.get(the_class = now_class, author = x).id)
                })
            else :
                people.append({
                    'name' : x.teacher_name,
                })
        return render(request, 'high/observation_record_all.html', { 'people' : people })

class observation_one_view(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        try:
            now_record = Observation_record.objects.get(pk = no)
        except :
            return render(request, 'high/observation_record_detail.html', { 'message': '錯誤' })
        if now_record.the_class.teach_teacher != request.user and now_record.author != request.user and request.user.power == False :  # 沒權限
            return HttpResponseRedirect('/')
        return render(request, 'high/observation_record_detail.html',{
            'author' : now_record.author,
            'observation_date' : now_record.observation_date,
            'teach_teacher' : now_record.teach_teacher,
            'subject' : now_record.subject,
            'class_name' : now_record.class_name,
            'learning_atmosphere' : now_record.learning_atmosphere,
            'learning_process' : now_record.learning_process,
            'learning_result' : now_record.learning_result,
            'experience_and_learning' : now_record.experience_and_learning,
        })

class briefing_view(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseRedirect('/')
        if now_class.teach_teacher != request.user and request.user.power == False : # 沒權限
            return HttpResponseRedirect('/')
        if Briefing_record.objects.filter(the_class = now_class).count() > 0 : #取得議課紀錄表
            now_record = Briefing_record.objects.get(the_class = now_class)
            return render(request, 'high/briefing_record_detail.html',{
                'observer' : now_record.observer,
                'teach_teacher' : now_record.teach_teacher,
                'briefing_date' : now_record.briefing_date,
                'briefing_time' : now_record.briefing_time, 
                'affirmation_teaching_performance' : now_record.affirmation_teaching_performance,
                'guide_discussion_teaching_performance' : now_record.guide_discussion_teaching_performance, 
                'judgment_performance' : now_record.judgment_performance, 
                'suggest' : now_record.suggest, 
                'growth_activity' : now_record.growth_activity
            })
        else :
            return render(request, 'high/observation_record_detail.html', { 'message': '錯誤' })

class preparation_view(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseRedirect('/')
        if Preparation_record.objects.filter(the_class = now_class).count() > 0 : #取得備課記錄表
            now_record = Preparation_record.objects.get(the_class = now_class)
        else :
            return render(request, 'high/observation_record_detail.html', { 'message': '錯誤' })
        if now_record.the_class.teach_teacher != request.user and request.user not in now_record.the_class.attend_data.attend_people.all() and request.user.power == False : # 沒權限
            return HttpResponseRedirect('/')
        return render(request, 'high/preparation_record_detail.html',{
                'subject' : now_record.subject,
                'author' : now_record.author,
                'date' : now_record.teach_date, 
                'start_time': now_record.teach_start_time,
                'end_time' : now_record.teach_end_time ,
                'teaching_grade' : now_record.teaching_grade, 
                'class_name' : now_record.class_name,
                'teach_teacher' : now_record.teach_teacher,
                'teaching_material' : now_record.source_of_teaching_material,
                'content' : now_record.content, 
                'teaching_objectives' : now_record.teaching_objectives,
                'student_experience' : now_record.student_experience, 
                'teaching_activity' : now_record.teaching_activity, 
                'evaluation_method' : now_record.evaluation_method
            })

class design_table_view(View) :
    def get(self, request, no) :
        if request.user.is_authenticated == False:  #未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseRedirect('/')
        if Design_table.objects.filter(the_class = now_class).count() > 0 : #取得教學活動設計表
            now_table = Design_table.objects.get(the_class = now_class)
        else :
            return render(request, 'high/observation_record_detail.html', { 'message': '錯誤' })
        if now_table.the_class.teach_teacher != request.user and request.user not in now_table.the_class.attend_data.attend_people.all() and request.user.power == False : # 沒權限
            return HttpResponseRedirect('/')
        return render(request, 'high/design_table_detail.html',{
                'class_name' : now_table.class_name ,
                'teach_teacher' : now_table.teach_teacher,
                'teach_class' :  now_table.teach_class ,
                'teaching_material' : now_table.source_of_teaching_material ,
                'date' : now_table.teach_date, 
                'start_time': now_table.teach_start_time,
                'end_time' : now_table.teach_end_time ,
                'background_analysis' : now_table.background_analysis,
                'big_teaching_method' : now_table.teaching_method,
                'teaching_resources' : now_table.teaching_resources,
                'reference_material' : now_table.reference_material,
                'big_teaching_objectives' : now_table.teaching_objectives,
                'detail' : Design_table_datail.objects.filter(the_design = now_table).all()
            })

class admin(View):
    calendar_link = 'http://www.google.com/calendar/event?action=TEMPLATE&text=公開授課（'
    def get(self, request) :
        if request.user.is_authenticated == False: # 未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        if request.user.power == False : # 沒權限
            return HttpResponseRedirect('/')
        all_class = list()
        for x in list(Class.objects.all()) :
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
                'attend_qr' : 'https://api.qrserver.com/v1/create-qr-code/?size=500x500&data=' + settings.HOST_NAME  + '/class/high/attend/' + str(x.id) + '/' + x.attend_data.attend_password +'&format=png',
                'observation' : '/class/high/observation/all/view/' + str(x.id),
                'check' : '/class/high/check/' + str(x.id),
                'link' : self.calendar_link + x.teach_teacher.teacher_name + '）' + '&dates=' + datelink + startlink + '/' + datelink + endlink + '&details=' + x.teach_teacher.teacher_department + x.subject + '公開授課%0A授課老師：' + x.teach_teacher.teacher_name + '&location=' + x.class_room + '&trp=false'
            })
            if Design_table.objects.filter(the_class = x).count() > 0 :
                all_class[-1]['design'] = '/class/high/design/view/' + str(x.id)
            if Preparation_record.objects.filter(the_class = x).count() > 0 :
                all_class[-1]['preparation'] = '/class/high/preparation/view/' + str(x.id)
            if Briefing_record.objects.filter(the_class = x).count() > 0 :
                all_class[-1]['briefing'] = '/class/high/briefing/view/' + str(x.id)
        return render(request, 'class/admin.html',{ 'all_class' : all_class })

class check(View) :
    def get(self, request, no):
        if request.user.is_authenticated == False: # 未登入
            return HttpResponseRedirect('/account/login')
        if request.user.teacher_name == '' or request.user.teacher_subject == '' or request.user.teacher_department == '': # 未註冊
            return HttpResponseRedirect('/account/create')
        if request.user.power == False : # 沒權限
            return HttpResponseRedirect('/')
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseRedirect('/')
        record, people = dict(), list()
        if Design_table.objects.filter(the_class = now_class).count() > 0 :
            record['design'] = '/class/high/design/view/' + str(no)
        if Preparation_record.objects.filter(the_class = now_class).count() > 0 :
            record['preparation'] = '/class/high/preparation/view/' + str(no)
        if Briefing_record.objects.filter(the_class = now_class).count() > 0 :
            record['briefing'] = '/class/high/briefing/view/' + str(no)
        for x in now_class.attend_data.attend_people.all() :
            if Observation_record.objects.filter(the_class = now_class, author = x).count() > 0 :
                people.append({
                    'name' : x.teacher_name,
                    'link' : '/class/high/observation/one/view/' + str(Observation_record.objects.get(the_class = now_class, author = x).id)
                })
            else :
                people.append({
                    'name' : x.teacher_name,
                })
        return render(request, 'class/check.html',{ 'class' : record, 'people' : people, 'link' : now_class.teaching_photo })
    def post(self, request, no) :
        if request.POST['link'] == '' :
            return render(request, 'class/check.html', { 'message': '未填寫' })
        try:
            now_class = Class.objects.get(pk = no)# 取得課程
        except :
            return HttpResponseRedirect('/')
        try:
            now_class.teaching_photo = request.POST['link']
            now_class.save()
        except :
            return render(request, 'class/check.html', { 'message': '錯誤' })
        return render(request, 'class/success.html')