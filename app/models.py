from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxLengthValidator, MinLengthValidator

# Create your models here.


class Hospital(models.Model):
    hospital_no = models.IntegerField(
        primary_key=True, validators=[MinValueValidator(1)])
    hospital_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    
    def __str__(self):
        return f'No. {self.hospital_no} {self.hospital_name}'
    
    def save(self, *args, **kwargs):
        if not len(Administration.objects.filter(hospital=self)) > 0:
            super().save(*args, **kwargs)
            administration = Administration(hospital=self, department_name='Administration')
            administration.save()
        if not len(Economic.objects.filter(hospital=self)) > 0:
            super().save(*args, **kwargs)
            economic = Economic(hospital=self, department_name='Economic')
            economic.save()
        super().save(*args, **kwargs)


class Department(models.Model):
    class Meta:
        unique_together = (('hospital', 'department_name'))

    hospital = models.ForeignKey(to=Hospital, on_delete=models.CASCADE)
    department_name = models.CharField(max_length=255)
    
    def __str__(self):
        return f'{self.department_name} department of {self.hospital}'


class Employee(AbstractUser):
    department = models.ForeignKey(
        to=Department, on_delete=models.SET_NULL, null=True)
    employee_type = models.CharField(max_length=255)

    description = models.TextField(max_length=1000, blank=True, null=True)
    
    class Meta:
        verbose_name = 'Employee'
    
    def __str__(self):
        return f'Doctor {self.first_name} {self.last_name}'


class Patient(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    
    ID = models.CharField(primary_key=True, max_length=12, validators=[MinLengthValidator(12)])
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Salary(models.Model):
    employee = models.OneToOneField(to=Employee, on_delete=models.CASCADE)
    value = models.FloatField(validators=[MinValueValidator(0)])
    
    def __str__(self):
        return f'{self.employee}\'s salary'


class Doctor(Employee):
    cabinet_number = models.IntegerField()
    rank = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Doctor'

    def save(self, *args, **kwargs):
        try:
            calendar = self.calendar
        except: 
            super().save(*args, **kwargs)
            calendar = Calendar(doctor=self)
            calendar.save()
        try:
            self.salary.value = 250000+self.rank*8000
            self.salary.save()
        except: 
            super().save(*args, **kwargs)
            salary = Salary(employee=self, value=(250000+self.rank*8000))
            salary.save()
        super().save(*args, **kwargs)


class Nurse(Employee):
    senior_doctor = models.ForeignKey(
        to=Doctor, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Nurse'


class Calendar(models.Model):
    doctor = models.OneToOneField(
        to=Doctor, on_delete=models.CASCADE, primary_key=True)
    
    
    def __str__(self):
        return f'{self.doctor}\'s calendar'


class Registration(models.Model):
    calendar = models.ForeignKey(to=Calendar, on_delete=models.CASCADE, related_name='registrations')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        if self.start_time > self.end_time:
            raise AssertionError('Invalid time range.')

        if not (9 <= self.start_time.hour < 18 and (9 <= self.end_time.hour < 18 or (self.end_time.hour == 18 and self.end_time.minute == 0))):
            raise AssertionError('Time range must be in the working time.')

        calendar_set = self.calendar.registrations.filter(
            start_time__range=(self.start_time, self.end_time))
        if len(calendar_set) > 0:
            if not (len(calendar_set) == 1 and calendar_set.first() == self):
                raise AssertionError('This time is corrupted already.')

        calendar_set = self.calendar.registrations.filter(
            end_time__range=(self.start_time, self.end_time))
        if len(calendar_set) > 0:
            if not (len(calendar_set) == 1 and calendar_set.first() == self):
                raise AssertionError('This time is corrupted already.')
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'Registration on {self.patient} {self.start_time} to {self.calendar.doctor}'


class Examination(models.Model):
    description = models.CharField(max_length=255)
    doctor = models.ForeignKey(to=Doctor, on_delete=models.SET_NULL, null=True)
    patient = models.ForeignKey(to=Patient, on_delete=models.SET_NULL, null=True)
    condition = models.TextChoices('Condition', 'SATISFACTORY MEDIUM SERIOUS TERMINAL')


class Diagnose(models.Model):
    base = models.ForeignKey(to=Examination, null=True,
                             on_delete=models.SET_NULL)


class MedicamentFirm(models.Model):
    name = models.CharField(max_length=255, unique=True)

class Medicament(models.Model):
    name = models.CharField(max_length=255)
    instruction = models.TextField()
    price = models.FloatField(validators=[MinValueValidator(0)])
    firm = models.ForeignKey(to=MedicamentFirm, on_delete=models.SET_NULL, null=True)


class Treatment(models.Model):
    description = models.TextField()
    diagnose = models.ForeignKey(to=Diagnose, null=True, on_delete=models.SET_NULL)
    patient = models.ForeignKey(to=Patient, null=True, on_delete=models.SET_NULL)


class TreatmentMedicament(Medicament):
    treatment = models.ForeignKey(to=Treatment, on_delete=models.CASCADE, related_name='medicaments')


class Referral(models.Model):
    From = models.ForeignKey(to=Doctor, on_delete=models.SET_NULL, null=True, related_name='sent_referrals')
    to = models.ForeignKey(to=Doctor, on_delete=models.SET_NULL, null=True, related_name='incoming_referrals')


class Administration(Department):
    head_doctor = models.ForeignKey(
        to=Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    department_name = 'Administration'
    
    def save(self, *args, **kwargs):
        if (not self.head_doctor) and len(Doctor.objects.all()) > 0:
            self.head_doctor = Doctor.objects.order_by('-rank')[0]
        super().save(*args, **kwargs)


class Economic(Department):
    department_name = 'Economic'


class Equipment(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)


class Discharge(models.Model):
    date = models.DateField()
    patient = models.ForeignKey(to=Patient, on_delete=models.CASCADE)
    hospital = models.ForeignKey(to=Hospital, on_delete=models.SET_NULL, null=True)


exports = [
    Hospital,
    Department,
    Employee,
    Patient,
    Salary,
    Doctor,
    Nurse,
    Calendar,
    Registration,
    Examination,
    Diagnose,
    MedicamentFirm,
    Medicament,
    Treatment,
    TreatmentMedicament,
    Referral,
    Administration,
    Economic,
    Equipment,
    Discharge
]
