def main():
    from app.models import Doctor, Hospital, Department, Patient, Administration
    import json
    from random import randint
    
    f = open('mock.json')
    data = json.load(f)

    department_names = [
        'Surgery',
        'Traumatic',
        'Generic',
        'Pediatric',
        'Special'
    ]

    def get_username(s):
        return s.lower().replace('’', '').replace('.', '').replace(' ', '_')


    for i, hospital in enumerate(data['hospitals']):
        try:
            h = Hospital(hospital_name=hospital['name'], location=hospital['location'], hospital_no=i+2)
        except:
            continue
        print(h)
        h.save()
        print('!!!!!')
        for department in department_names:
            d = Department(hospital=h, department_name=department)
            d.save()
        for j, doctor in enumerate(data['doctors'][i*10:(i+1)*10]):
            dep_name = department_names[randint(0, 4)]
            dep = Department.objects.filter(hospital=h, department_name=dep_name).first()
            if not dep:
                continue
            d = Doctor(
                password='Admin123', 
                username=get_username(doctor['first_name'] + ' ' + doctor['last_name']), 
                first_name=doctor['first_name'], 
                last_name=doctor['last_name'], 
                department=dep, 
                employee_type='Doctor', 
                cabinet_number="%02d"%(j), 
                rank=randint(5, 120)
                )
            d.save()
        Administration.objects.filter(hospital=h).first().save()

    for count, patient in enumerate(data['patients']):
        p = Patient(first_name=patient['first_name'], last_name=patient['last_name'], ID="%012d"%(count))
        p.save()

    f.close()