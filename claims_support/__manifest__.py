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
        'views/nps_survey_views.xml',
        'views/claims_support_views.xml',
        'views/res_config_settings_views.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/claims_support_data.xml',
        'data/ir_sequence.xml',
            
    ],
}