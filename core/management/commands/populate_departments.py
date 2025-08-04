from django.core.management.base import BaseCommand
from core.models import Department, Branch

class Command(BaseCommand):
    help = 'Populate database with initial department and branch data'

    def handle(self, *args, **options):
        self.stdout.write('Populating departments and branches...')
        
        # Department and Branch data
        departments_data = {
            'Computer Science & Engineering': {
                'code': 'CSE',
                'branches': [
                    {'name': 'Artificial Intelligence', 'code': 'AI'},
                    {'name': 'Machine Learning', 'code': 'ML'},
                    {'name': 'Data Science', 'code': 'DS'},
                    {'name': 'Cybersecurity', 'code': 'CS'},
                    {'name': 'Software Engineering', 'code': 'SE'},
                    {'name': 'Web Development', 'code': 'WD'},
                    {'name': 'Mobile App Development', 'code': 'MAD'},
                    {'name': 'Computer Networks', 'code': 'CN'},
                    {'name': 'Database Systems', 'code': 'DBS'},
                    {'name': 'Computer Graphics', 'code': 'CG'},
                ]
            },
            'Electronics & Communication Engineering': {
                'code': 'ECE',
                'branches': [
                    {'name': 'VLSI Design', 'code': 'VLSI'},
                    {'name': 'Embedded Systems', 'code': 'ES'},
                    {'name': 'Signal Processing', 'code': 'SP'},
                    {'name': 'Communication Systems', 'code': 'COM'},
                    {'name': 'Microelectronics', 'code': 'ME'},
                    {'name': 'RF Engineering', 'code': 'RF'},
                    {'name': 'Control Systems', 'code': 'CS'},
                    {'name': 'Digital Electronics', 'code': 'DE'},
                ]
            },
            'Electrical Engineering': {
                'code': 'EE',
                'branches': [
                    {'name': 'Power Systems', 'code': 'PS'},
                    {'name': 'Power Electronics', 'code': 'PE'},
                    {'name': 'Control Systems', 'code': 'CS'},
                    {'name': 'Electrical Machines', 'code': 'EM'},
                    {'name': 'Renewable Energy', 'code': 'RE'},
                    {'name': 'High Voltage Engineering', 'code': 'HV'},
                    {'name': 'Electric Drives', 'code': 'ED'},
                ]
            },
            'Mechanical Engineering': {
                'code': 'ME',
                'branches': [
                    {'name': 'Thermal Engineering', 'code': 'TE'},
                    {'name': 'Manufacturing Engineering', 'code': 'MFE'},
                    {'name': 'Design Engineering', 'code': 'DE'},
                    {'name': 'Automotive Engineering', 'code': 'AE'},
                    {'name': 'Aerospace Engineering', 'code': 'ASE'},
                    {'name': 'Robotics', 'code': 'ROB'},
                    {'name': 'Materials Engineering', 'code': 'MAT'},
                    {'name': 'Fluid Mechanics', 'code': 'FM'},
                ]
            },
            'Civil Engineering': {
                'code': 'CE',
                'branches': [
                    {'name': 'Structural Engineering', 'code': 'SE'},
                    {'name': 'Geotechnical Engineering', 'code': 'GE'},
                    {'name': 'Transportation Engineering', 'code': 'TE'},
                    {'name': 'Environmental Engineering', 'code': 'EE'},
                    {'name': 'Water Resources Engineering', 'code': 'WRE'},
                    {'name': 'Construction Management', 'code': 'CM'},
                    {'name': 'Urban Planning', 'code': 'UP'},
                ]
            },
            'Chemical Engineering': {
                'code': 'CHE',
                'branches': [
                    {'name': 'Process Engineering', 'code': 'PE'},
                    {'name': 'Petrochemical Engineering', 'code': 'PCE'},
                    {'name': 'Biochemical Engineering', 'code': 'BE'},
                    {'name': 'Environmental Engineering', 'code': 'EE'},
                    {'name': 'Materials Engineering', 'code': 'ME'},
                    {'name': 'Food Engineering', 'code': 'FE'},
                ]
            },
            'Information Technology': {
                'code': 'IT',
                'branches': [
                    {'name': 'Software Development', 'code': 'SD'},
                    {'name': 'Network Administration', 'code': 'NA'},
                    {'name': 'Database Administration', 'code': 'DBA'},
                    {'name': 'Information Security', 'code': 'IS'},
                    {'name': 'Cloud Computing', 'code': 'CC'},
                    {'name': 'DevOps', 'code': 'DO'},
                    {'name': 'IT Consulting', 'code': 'ITC'},
                ]
            },
            'Biotechnology': {
                'code': 'BT',
                'branches': [
                    {'name': 'Medical Biotechnology', 'code': 'MBT'},
                    {'name': 'Agricultural Biotechnology', 'code': 'ABT'},
                    {'name': 'Industrial Biotechnology', 'code': 'IBT'},
                    {'name': 'Environmental Biotechnology', 'code': 'EBT'},
                    {'name': 'Bioinformatics', 'code': 'BI'},
                    {'name': 'Genetic Engineering', 'code': 'GE'},
                ]
            },
            'Mathematics': {
                'code': 'MATH',
                'branches': [
                    {'name': 'Pure Mathematics', 'code': 'PM'},
                    {'name': 'Applied Mathematics', 'code': 'AM'},
                    {'name': 'Statistics', 'code': 'STAT'},
                    {'name': 'Mathematical Modeling', 'code': 'MM'},
                    {'name': 'Numerical Analysis', 'code': 'NA'},
                    {'name': 'Operations Research', 'code': 'OR'},
                ]
            },
            'Physics': {
                'code': 'PHY',
                'branches': [
                    {'name': 'Theoretical Physics', 'code': 'TP'},
                    {'name': 'Experimental Physics', 'code': 'EP'},
                    {'name': 'Astrophysics', 'code': 'AP'},
                    {'name': 'Nuclear Physics', 'code': 'NP'},
                    {'name': 'Condensed Matter Physics', 'code': 'CMP'},
                    {'name': 'Quantum Physics', 'code': 'QP'},
                ]
            },
            'Chemistry': {
                'code': 'CHEM',
                'branches': [
                    {'name': 'Organic Chemistry', 'code': 'OC'},
                    {'name': 'Inorganic Chemistry', 'code': 'IC'},
                    {'name': 'Physical Chemistry', 'code': 'PC'},
                    {'name': 'Analytical Chemistry', 'code': 'AC'},
                    {'name': 'Biochemistry', 'code': 'BC'},
                    {'name': 'Environmental Chemistry', 'code': 'EC'},
                ]
            },
            'Business Administration': {
                'code': 'BBA',
                'branches': [
                    {'name': 'Finance', 'code': 'FIN'},
                    {'name': 'Marketing', 'code': 'MKT'},
                    {'name': 'Human Resources', 'code': 'HR'},
                    {'name': 'Operations Management', 'code': 'OM'},
                    {'name': 'International Business', 'code': 'IB'},
                    {'name': 'Entrepreneurship', 'code': 'ENT'},
                    {'name': 'Digital Marketing', 'code': 'DM'},
                ]
            }
        }
        
        created_departments = 0
        created_branches = 0
        
        for dept_name, dept_info in departments_data.items():
            # Create or get department
            department, created = Department.objects.get_or_create(
                name=dept_name,
                defaults={
                    'code': dept_info['code'],
                    'description': f'Department of {dept_name}'
                }
            )
            
            if created:
                created_departments += 1
                self.stdout.write(f'Created department: {dept_name}')
            
            # Create branches for this department
            for branch_info in dept_info['branches']:
                branch, created = Branch.objects.get_or_create(
                    name=branch_info['name'],
                    department=department,
                    defaults={
                        'code': branch_info['code'],
                        'description': f'{branch_info["name"]} specialization in {dept_name}'
                    }
                )
                
                if created:
                    created_branches += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated {created_departments} departments and {created_branches} branches'
            )
        )