{
    'name': 'Lunch Management',
    'version': '19.0.0.1',
    'sequence': '-1',
    'summary': 'Track employee lunch details and costs',
    'description': 'Record and manage daily lunch data for employees.',
    'category': 'Human Resources',
    'author': 'Mohit Chand',

    'images': ['static/description/icon.png'],
    'depends': ['base','hr'],
    'data': [
        
        'security/ir.model.access.csv',
        'views/lunch_record_views.xml',
        'views/lunch_report_views.xml',
        'reports/lunch_report.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
