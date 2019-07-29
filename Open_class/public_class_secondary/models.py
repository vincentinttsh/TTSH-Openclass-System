from django.db import models
from django.contrib import admin
from account.models import User

class Attend_data(models.Model) :
    attend_password = models.CharField(max_length = 10, verbose_name='參加密碼')
    attend_number = models.IntegerField(default=0, verbose_name='參加人數')
    attend_people = models.ManyToManyField(User, verbose_name='參加的人',related_name='attend_class')
    class Meta:
        verbose_name, verbose_name_plural = '國中公開觀課報名人數', '國中公開觀課報名人數'
    def __str__(self):
        return self.the_class.teach_teacher.teacher_name + '-' + self.the_class.subject
@admin.register(Attend_data)
class Attend_dataAdmin(admin.ModelAdmin):
    pass

class Secondary_Class(models.Model) :
    teach_teacher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='老師')
    subject = models.CharField(max_length = 20, verbose_name='上課科目')
    class_room = models.CharField(max_length = 10, verbose_name='上課教室')
    teach_date = models.DateField(verbose_name='上課日期')
    teach_start_time = models.TimeField(verbose_name='上課開始時間')
    teach_end_time = models.TimeField(verbose_name='上課結束時間')
    teaching_photo = models.URLField(verbose_name='上課照片', default = '')
    attend_data = models.OneToOneField(Attend_data, on_delete=models.CASCADE, verbose_name='參加資料', related_name='the_class')
    class Meta:
        verbose_name, verbose_name_plural = '國中公開觀課報名資料', '國中公開觀課報名資料'
    def __str__(self):
        return self.teach_teacher.teacher_name + '-' + self.subject

@admin.register(Secondary_Class)
class Secondary_ClassAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Secondary_Class._meta.fields]
    search_fields = ('teach_teacher', 'subject', 'class_room', 'teach_date', 'teach_start_time', 'teach_end_time')
    ordering = ('teach_date', 'teach_start_time', 'teach_end_time', 'teach_teacher')

class Design_table(models.Model) :
    class_name = models.CharField(max_length = 20, verbose_name='單元名稱')
    teach_teacher = models.CharField(max_length = 6, verbose_name='授課老師')
    teach_class = models.CharField(max_length = 20, verbose_name='授課班級')
    teaching_objectives = models.TextField(verbose_name='教學目標')
    the_class = models.ForeignKey(Secondary_Class, on_delete=models.CASCADE, verbose_name='課程')
    class Meta:
        verbose_name, verbose_name_plural = '國中課程教學活動設計表', '國中課程教學活動設計表'
    def __str__(self):
        return self.the_class.teach_teacher.teacher_name + '-' + self.the_class.subjects

@admin.register(Design_table)
class Design_tableAdmin(admin.ModelAdmin):
    list_display = ['class_name', 'teach_class', 'teach_teacher']
    search_fields = ('class_name', 'teach_class', 'teach_teacher')
    ordering = ('teach_teacher',)

class Design_table_datail(models.Model) :
    teaching_activity = models.TextField(verbose_name='教學活動')
    teaching_aid = models.TextField(verbose_name='使用教具')
    assessment_method = models.TextField(verbose_name='評量方式')
    teaching_method = models.TextField(verbose_name='教學方法')
    time_allocation = models.TextField(verbose_name='時間分配')
    the_design = models.ForeignKey(Design_table, on_delete=models.CASCADE, verbose_name='課程教學活動設計表')
    class Meta:
        verbose_name, verbose_name_plural = '國中課程教學活動設計表下方表格', '國中課程教學活動設計表下方表格'
    def __str__(self):
        return self.the_design.teach_teacher + '-' + self.the_design.class_name

@admin.register(Design_table_datail)
class Design_table_datailAdmin(admin.ModelAdmin):
    pass

class Preparation_record(models.Model) :
    teach_date = models.DateField(verbose_name='教學日期')
    teach_start_time = models.TimeField(verbose_name='教學開始時間')
    teach_end_time = models.TimeField(verbose_name='教學結束時間')
    teaching_grade = models.CharField(max_length = 20, verbose_name='教學年級')
    class_name = models.CharField(max_length = 20, verbose_name='教學單元')
    teaching_sessions = models.IntegerField(verbose_name='教學節數')
    teach_teacher = models.CharField(max_length = 6, verbose_name='教學者')
    source_of_teaching_material = models.CharField(max_length = 20, verbose_name='教材來源')
    content = models.TextField(verbose_name='教材內容')
    teaching_objectives = models.TextField(verbose_name='教學目標')
    student_experience = models.TextField(verbose_name='學生經驗或學習背景分析')
    teaching_activity = models.TextField(verbose_name='教學活動')
    evaluation_method = models.TextField(verbose_name='學生學習成效評估方式')
    the_class = models.ForeignKey(Secondary_Class, on_delete=models.CASCADE, verbose_name='課程')
    class Meta:
        verbose_name, verbose_name_plural = '國中共同備課記錄表', '國中共同備課記錄表'
    def __str__(self):
        return self.the_class.teach_teacher + '-' + self.the_class.subject

@admin.register(Preparation_record)
class Preparation_recordAdmin(admin.ModelAdmin) :
    list_display = ['class_name', 'teach_teacher', 'teach_date', 'teach_start_time', 'teach_end_time',]
    search_fields = ('class_name', 'teach_teacher', 'teach_date')
    ordering = ('teach_date', 'teach_start_time', 'teach_end_time', 'teach_teacher')

class Observation_record(models.Model) :
    the_class = models.ForeignKey(Secondary_Class, on_delete=models.CASCADE, verbose_name='課程')
    context = models.TextField(verbose_name='摘記')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='填表人', related_name='class_observation')
    observation_date = models.DateField(verbose_name='觀課日期')
    teach_teacher = models.CharField(max_length = 6, verbose_name='授課教師')
    subject = models.CharField(max_length = 20, verbose_name='科目')
    teach_class = models.CharField(max_length = 20, verbose_name='觀課班級')
    # 教學策略
    teaching_strategy_1 = models.IntegerField(verbose_name='要求學生參與教學活動-量化結果')
    teaching_strategy_1_text = models.TextField(verbose_name='要求學生參與教學活動-質性描述')
    teaching_strategy_2 = models.IntegerField(verbose_name='延伸學生的反應或表現-量化結果')
    teaching_strategy_2_text = models.TextField(verbose_name='延伸學生的反應或表現-質性描述')
    teaching_strategy_3 = models.IntegerField(verbose_name='在學習活動進行中掌握學生的表現-量化結果')
    teaching_strategy_3_text = models.TextField(verbose_name='在學習活動進行中掌握學生的表現-質性描述')
    teaching_strategy_4 = models.IntegerField(verbose_name='提供正確的回饋或修正，澄清學生錯誤的觀念-量化結果')
    teaching_strategy_4_text = models.TextField(verbose_name='提供正確的回饋或修正，澄清學生錯誤的觀念-質性描述')
    # 教室經營與管理
    classroom_management_1 = models.IntegerField(verbose_name='善用有助於教學的管理步驟與常規-量化結果')
    classroom_management_1_text = models.TextField(verbose_name='善用有助於教學的管理步驟與常規-質性描述')
    classroom_management_2 = models.IntegerField(verbose_name='能進行適當有序的教學活動，能調整上課速度-量化結果')
    classroom_management_2_text = models.TextField(verbose_name='能進行適當有序的教學活動，能調整上課速度-質性描述')
    classroom_management_3 = models.IntegerField(verbose_name='將重點放在教學目標上並掌握學生的注意力-量化結果')
    classroom_management_3_text = models.TextField(verbose_name='將重點放在教學目標上並掌握學生的注意力-質性描述')
    classroom_management_4 = models.IntegerField(verbose_name='妥善處理學生不當行為-量化結果')
    classroom_management_4_text = models.TextField(verbose_name='妥善處理學生不當行為-質性描述')
    # 呈現主題
    presenting_1 = models.IntegerField(verbose_name='循序漸進由簡而繁有組織的呈現教材內容-量化結果')
    presenting_1_text = models.TextField(verbose_name='循序漸進由簡而繁有組織的呈現教材內容-質性描述')
    presenting_2 = models.IntegerField(verbose_name='運用概念、定義、例證說明-量化結果')
    presenting_2_text = models.TextField(verbose_name='運用概念、定義、例證說明-質性描述')
    presenting_3 = models.IntegerField(verbose_name='依據教學需要適切的運用教學媒體-量化結果')
    presenting_3_text = models.TextField(verbose_name='依據教學需要適切的運用教學媒體-質性描述')
    presenting_4 = models.IntegerField(verbose_name='適切提供練習或作業，引導學生精熟學習-量化結果')
    presenting_4_text = models.TextField(verbose_name='適切提供練習或作業，引導學生精熟學習-質性描述')
    # 學習環境
    learning_environment_1 = models.IntegerField(verbose_name='給予學生適當的挑戰-量化結果')
    learning_environment_1_text = models.TextField(verbose_name='給予學生適當的挑戰-質性描述')
    learning_environment_2 = models.IntegerField(verbose_name='教師在教學中表現熱忱、給予學生關切、鼓勵學生表達-量化結果') 
    learning_environment_2_text = models.TextField(verbose_name='教師在教學中表現熱忱、給予學生關切、鼓勵學生表達-質性描述')
    learning_environment_3 = models.IntegerField(verbose_name='形成積極參與的學習氣氛、引導合作學習的同儕互動關係-量化結果')
    learning_environment_3_text = models.TextField(verbose_name='形成積極參與的學習氣氛、引導合作學習的同儕互動關係-質性描述')
    learning_environment_4 = models.IntegerField(verbose_name='建立互信相互尊重的班級氣氛-量化結果')
    learning_environment_4_text = models.TextField(verbose_name=' 建立互信相互尊重的班級氣氛-質性描述')
    class Meta:
        verbose_name, verbose_name_plural = '國中公開觀課紀錄表', '國中公開觀課紀錄表'
    def __str__(self):
        return self.the_class.teach_teacher + '-' + self.the_class.subject

@admin.register(Observation_record)
class Observation_recordAdmin(admin.ModelAdmin) :
    list_display = ['subject', 'teach_class', 'author', 'teach_teacher', 'observation_date']
    search_fields = ('subject', 'author', 'teach_teacher', 'observation_date', 'teach_class')
    ordering = ('observation_date',)

class Briefing_record(models.Model) :
    teach_teacher = models.CharField(max_length = 6, verbose_name='教學者')
    observer = models.TextField(verbose_name='觀察者')
    briefing_date = models.DateField(verbose_name='議課日期')
    briefing_time = models.TimeField(verbose_name='議課時間')
    advantages_and_features = models.TextField(verbose_name='教與學之優點及特色')
    adjust_or_change = models.TextField(verbose_name='教與學待調整或改變之處')
    learning_and_harvesting = models.TextField(verbose_name='回饋人員的學習與收穫')
    the_class = models.ForeignKey(Secondary_Class, on_delete=models.CASCADE, verbose_name='課程')
    class Meta:
        verbose_name, verbose_name_plural = '國中共同議課紀錄表', '國中共同議課紀錄表'
    def __str__(self):
        return self.the_class.teach_teacher + '-' + self.the_class.subject


@admin.register(Briefing_record)
class Briefing_recordAdmin(admin.ModelAdmin) :
    list_display = ['teach_teacher', 'observer', 'briefing_date', 'briefing_time']
    search_fields = ('teach_teacher', 'observer', 'briefing_date', 'briefing_time')
    ordering = ('briefing_date', 'briefing_time')

class Growth_plan(models.Model) :
    growth_mode = models.CharField(max_length = 50, verbose_name='成長方式')
    abstract = models.CharField(max_length = 50, verbose_name='內容概要說明')
    member = models.TextField(verbose_name='協助或合作人員')
    done_date = models.DateField(verbose_name='預計完成日期')
    the_briefing = models.ForeignKey(Briefing_record, on_delete=models.CASCADE, verbose_name='議課紀錄表')
    class Meta:
        verbose_name, verbose_name_plural = '授課教師預定專業成長計畫', '授課教師預定專業成長計畫'
    def __str__(self):
        return self.the_briefing.the_class.teach_teacher + '-' + self.the_briefing.the_class.subject

@admin.register(Growth_plan)
class Growth_planAdmin(admin.ModelAdmin) :
    pass