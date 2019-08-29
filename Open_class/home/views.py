from django.shortcuts import render
from public_class_secondary.models import Secondary_Class as SClass
from public_class_high.models import High_Class as HClass
import datetime

def home(request):
    all_class = list()
    calendar_link = 'http://www.google.com/calendar/event?action=TEMPLATE&text=公開授課（'
    Class = HClass
    for x in list(Class.objects.filter(teach_date__gte = datetime.date.today()).order_by('teach_date')) :
        datelink = str(x.teach_date).replace('-', '') + 'T' # 轉日期格式 YYYY-MM-DD to YYYYMMDD
        startlink = str(x.teach_start_time).replace(':', '') # 轉時間格式 HH:MM:SS to HHMMSS
        endlink = str(x.teach_end_time).replace(':', '') # 轉時間格式 HH:MM:SS to HHMMSS
        department = x.teach_teacher.teacher_department # 部門
        all_class.append({
            'department' : department,
            'teacher' : x.teach_teacher.teacher_name,
            'subject' : x.subject,
            'classroom' : x.class_room,
            'date' : x.teach_date,
            'start_time' : x.teach_start_time,
            'end_time' : x.teach_end_time,
            'link' : calendar_link + x.teach_teacher.teacher_name + '）' + '&dates=' + datelink + startlink + '/' + datelink + endlink + '&details=' + x.teach_teacher.teacher_department + x.subject + '公開授課%0A授課老師：' + x.teach_teacher.teacher_name + '&location=' + x.class_room + '&trp=false'
        })
    Class = SClass
    for x in list(Class.objects.filter(teach_date__gte = datetime.date.today()).order_by('teach_date')) :
        datelink = str(x.teach_date).replace('-', '') + 'T' # 轉日期格式 YYYY-MM-DD to YYYYMMDD
        startlink = str(x.teach_start_time).replace(':', '') # 轉時間格式 HH:MM:SS to HHMMSS
        endlink = str(x.teach_end_time).replace(':', '') # 轉時間格式 HH:MM:SS to HHMMSS
        department = x.teach_teacher.teacher_department # 部門
        all_class.append({
            'department' : department,
            'teacher' : x.teach_teacher.teacher_name,
            'subject' : x.subject,
            'classroom' : x.class_room,
            'date' : x.teach_date,
            'start_time' : x.teach_start_time,
            'end_time' : x.teach_end_time,
            'link' : calendar_link + x.teach_teacher.teacher_name + '）' + '&dates=' + datelink + startlink + '/' + datelink + endlink + '&details=' + x.teach_teacher.teacher_department + x.subject + '公開授課%0A授課老師：' + x.teach_teacher.teacher_name + '&location=' + x.class_room + '&trp=false'
        })
    return render(request, 'home/home.html',{ 'all_class' : all_class })

