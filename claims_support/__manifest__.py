{
    'name': "Soporte de reclamaciones",
    'version': '1.0',
    'depends': ['base','rockys_helpdesk_complaints_book'],
    'installable': True,
    'application': True,
    'author': "JANAQ",
    'category': '',
    'summary': 'Módulo para el soporte de reclamaciones',
    'description': """
    Módulo diseñado para proporcionar una solución integral que permite tanto la recopilación y análisis de respuestas de encuestas NPS como la gestión eficiente de reclamaciones
    """,
    'data': [
        'security/ir_group.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'template/mail_template_send_customer.xml',
        'views/nps_survey_views.xml',
        'views/claims_support_views.xml',
        'views/res_config_settings_views.xml',
        'data/claims_support_data.xml',
        'data/ir_sequence.xml',
    ],
    "assets": {
        "web.assets_backend": [
            #MÓDULO
            "claims_support/static/src/xml/dashboard_nps.xml",
            "claims_support/static/src/js/dashboard_nps.js",
            #GRÁFICOS
            #"https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.3.2/chart.js",
            #SELECT
            "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css",
            "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js",
            #DATE
            "https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.min.js",
            #DOWLOAND
            "https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.4.1/jspdf.min.js",
            "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/0.5.0-alpha1/html2canvas.min.js",
        ],
    },
}