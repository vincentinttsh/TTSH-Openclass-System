from django.db import models
from django.contrib import admin
from account.models import User

class Able_Create(models.Model):
    class Meta:
        verbose_name, verbose_name_plural = '開放註冊課程', '開放註冊課程'
    mode = models.CharField(max_length=100, verbose_name="模式", default="default")
    able = models.BooleanField(default=True, verbose_name="開放註冊課程")
    def __str__(self):
        return self.mode

@admin.register(Able_Create)
class Able_CreateAdmin(admin.ModelAdmin):
    pass

class Attend_data(models.Model) :
    attend_password = models.CharField(max_length = 10, verbose_name='參加密碼')
    attend_number = models.IntegerField(default=0, verbose_name='參加人數')
    attend_people = models.ManyToManyField(User, verbose_name='參加的人', blank=True)
    class Meta:
        verbose_name, verbose_name_plural = '高中公開觀課報名人數', '高中公開觀課報名人數'
    def __str__(self):
        try :
            return self.the_class.teach_teacher.teacher_name + '-' + self.the_class.subject
        except :
            return "invalid data"
@admin.register(Attend_data)
class Attend_dataAdmin(admin.ModelAdmin):
    pass

class High_Class(models.Model) :
    teach_teacher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='老師')
    subject = models.CharField(max_length = 200, verbose_name='上課科目')
    class_room = models.CharField(max_length = 10, verbose_name='上課教室')
    teach_date = models.DateField(verbose_name='上課日期')
    teach_start_time = models.TimeField(verbose_name='上課開始時間')
    teach_end_time = models.TimeField(verbose_name='上課結束時間')
    teaching_photo = models.URLField(verbose_name='上課照片', default = '', blank=True)
    attend_data = models.OneToOneField(Attend_data, on_delete=models.CASCADE, verbose_name='參加資料', related_name='the_class')
    class Meta:
        verbose_name, verbose_name_plural = '高中公開觀課報名資料', '高中公開觀課報名資料'
    def __str__(self):
        return self.teach_teacher.teacher_name + '-' + self.subject

@admin.register(High_Class)
class High_ClassAdmin(admin.ModelAdmin):
    list_display = [field.name for field in High_Class._meta.fields]
    search_fields = ('teach_teacher', 'subject', 'class_room', 'teach_date', 'teach_start_time', 'teach_end_time')
    ordering = ('teach_date', 'teach_start_time', 'teach_end_time', 'teach_teacher')

class Design_table(models.Model) :
    class_name = models.CharField(max_length = 200, verbose_name='單元名稱')
    teach_teacher = models.CharField(max_length = 200, verbose_name='授課老師')
    source_of_teaching_material = models.CharField(max_length = 200, verbose_name='教材來源')
    teach_class = models.CharField(max_length = 200, verbose_name='授課班級')
    teach_date = models.DateField(verbose_name='教學日期')
    teach_start_time = models.TimeField(verbose_name='教學開始時間')
    teach_end_time = models.TimeField(verbose_name='教學結束時間')
    background_analysis = models.TextField(verbose_name='學生學習背景分析')
    teaching_method = models.TextField(verbose_name='教學方法')
    teaching_resources = models.TextField(verbose_name='教學資源')
    reference_material = models.TextField(verbose_name='參考資料')
    teaching_objectives = models.TextField(verbose_name='教學目標')
    the_class = models.ForeignKey(High_Class, on_delete=models.CASCADE, verbose_name='課程')
    class Meta:
        verbose_name, verbose_name_plural = '高中課程教學活動設計表', '高中課程教學活動設計表'
    def __str__(self):
        return self.the_class.teach_teacher.teacher_name + '-' + self.the_class.subject

@admin.register(Design_table)
class Design_tableAdmin(admin.ModelAdmin):
    list_display = ['class_name', 'teach_class', 'teach_teacher', 'teach_date', 'teach_start_time', 'teach_end_time',]
    search_fields = ('class_name', 'teach_class', 'teach_teacher', 'teach_date')
    ordering = ('teach_date', 'teach_start_time', 'teach_end_time', 'teach_teacher')

class Design_table_datail(models.Model) :
    teaching_objectives = models.TextField(verbose_name='教學目標')
    teacher_activity = models.TextField(verbose_name='教師活動')
    student_activities = models.TextField(verbose_name='學生活動')
    teaching_aid = models.TextField(verbose_name='使用教具')
    assessment_method = models.TextField(verbose_name='評量方式')
    teaching_method = models.TextField(verbose_name='教學方法')
    time_allocation = models.TextField(verbose_name='時間分配')
    the_design = models.ForeignKey(Design_table, on_delete=models.CASCADE, verbose_name='課程教學活動設計表')
    class Meta:
        verbose_name, verbose_name_plural = '高中課程教學活動設計表下方表格', '高中課程教學活動設計表下方表格'
    def __str__(self):
        return self.the_design.teach_teacher + '-' + self.the_design.class_name

@admin.register(Design_table_datail)
class Design_table_datailAdmin(admin.ModelAdmin):
    pass

class Preparation_record(models.Model) :
    subject = models.CharField(max_length = 200, verbose_name='學科')
    author = models.CharField(max_length = 200, verbose_name='填寫者')
    teach_date = models.DateField(verbose_name='教學日期')
    teach_start_time = models.TimeField(verbose_name='教學開始時間')
    teach_end_time = models.TimeField(verbose_name='教學結束時間')
    teaching_grade = models.CharField(max_length = 200, verbose_name='教學年級')
    class_name = models.CharField(max_length = 200, verbose_name='教學單元')
    teach_teacher = models.CharField(max_length = 20, verbose_name='教學者')
    source_of_teaching_material = models.CharField(max_length = 200, verbose_name='教材來源')
    content = models.TextField(verbose_name='教材內容')
    teaching_objectives = models.TextField(verbose_name='教學目標')
    student_experience = models.TextField(verbose_name='學生經驗')
    teaching_activity = models.TextField(verbose_name='教學活動')
    evaluation_method = models.TextField(verbose_name='學生學習成效評估方式')
    the_class = models.ForeignKey(High_Class, on_delete=models.CASCADE, verbose_name='課程')
    class Meta:
        verbose_name, verbose_name_plural = '高中共同備課記錄表', '高中共同備課記錄表'
    def __str__(self):
        return self.the_class.teach_teacher.teacher_name + '-' + self.the_class.subject

@admin.register(Preparation_record)
class Preparation_recordAdmin(admin.ModelAdmin) :
    list_display = ['subject', 'author', 'teach_teacher', 'teach_date', 'teach_start_time', 'teach_end_time',]
    search_fields = ('subject', 'author', 'teach_teacher', 'teach_date')
    ordering = ('teach_date', 'teach_start_time', 'teach_end_time', 'teach_teacher')

class Observation_record(models.Model) :
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='觀課者姓名')
    observation_date = models.DateField(verbose_name='觀課日期')
    teach_teacher = models.CharField(max_length = 20, verbose_name='教學者')
    subject = models.CharField(max_length = 200, verbose_name='科目')
    class_name = models.CharField(max_length = 200, verbose_name='單元名稱')
    learning_atmosphere = models.TextField(verbose_name='全班學習氣氛')
    learning_process = models.TextField(verbose_name='學生學習歷程')
    learning_result = models.TextField(verbose_name='學生學習結果')
    experience_and_learning = models.TextField(verbose_name='觀課的心得與學習')
    the_class = models.ForeignKey(High_Class, on_delete=models.CASCADE, verbose_name='課程')
    class Meta:
        verbose_name, verbose_name_plural = '高中公開觀課紀錄表', '高中公開觀課紀錄表'
    def __str__(self):
        return self.the_class.teach_teacher.teacher_name + '-' + self.the_class.subject

@admin.register(Observation_record)
class Observation_recordAdmin(admin.ModelAdmin) :
    list_display = ['subject', 'class_name', 'author', 'teach_teacher', 'observation_date']
    search_fields = ('subject', 'author', 'teach_teacher', 'observation_date', 'class_name')
    ordering = ('observation_date',)

class Briefing_record(models.Model) :
    teach_teacher = models.CharField(max_length = 20, verbose_name='教學者')
    observer = models.TextField(verbose_name='觀察者')
    briefing_date = models.DateField(verbose_name='議課日期')
    briefing_time = models.TimeField(verbose_name='議課時間')
    affirmation_teaching_performance = models.TextField(verbose_name='肯定教學表現')
    guide_discussion_teaching_performance = models.TextField(verbose_name='引導討論教學表現')
    judgment_performance = models.TextField(verbose_name='判斷表現程度')
    suggest = models.TextField(verbose_name='改進學生學習能力提供之建議')
    growth_activity = models.TextField(verbose_name='協助擬定成長活動')
    the_class = models.ForeignKey(High_Class, on_delete=models.CASCADE, verbose_name='課程')
    class Meta:
        verbose_name, verbose_name_plural = '高中共同議課紀錄表', '高中共同議課紀錄表'
    def __str__(self):
        return self.the_class.teach_teacher.teacher_name + '-' + self.the_class.subject

@admin.register(Briefing_record)
class Briefing_recordAdmin(admin.ModelAdmin) :
    list_display = ['teach_teacher', 'observer', 'briefing_date', 'briefing_time']
    search_fields = ('teach_teacher', 'observer', 'briefing_date', 'briefing_time')
    ordering = ('briefing_date', 'briefing_time')