from django.db import models

class AttendanceLog(models.Model):
    id = models.AutoField(primary_key=True)
    student_name = models.CharField(max_length=150)
    date = models.CharField(max_length=20)
    time = models.CharField(max_length=20)
    confidence = models.FloatField()
    image_path = models.TextField(null=True, blank=True)
    sync_status = models.IntegerField(default=0)

    class Meta:
        db_table = 'attendance_logs'
        managed = False  # SQLite DB table ကို local_storage.py က ထိန်းချုပ်ထားသောကြောင့်

    def __str__(self):
        return f"{self.student_name} - {self.date} {self.time}"