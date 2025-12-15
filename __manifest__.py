{
    'name': 'Lunch Management',
    'version': '19.0.0.1',
    'sequence': '-1',
    'summary': 'Track employee lunch details and costs',
    'description': 'Record and manage daily lunch data for employees.',
    'category': 'Human Resources',
    'author': 'Innovax Solutions Pvt Ltd',

    'images': ['static/description/icon.png'],
    'depends': ['base','hr','mail'],
    'data': [
        
        'security/ir.model.access.csv',
        'security/lunch_security.xml',
        'data/lunch_email_data.xml',
        'views/lunch_record_views.xml',
        'views/lunch_report_views.xml',
        'views/lunch_email_views.xml',
        'reports/lunch_report.xml',
    ],
    'external_dependencies': {
        'python': ['pandas', 'openpyxl'],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}