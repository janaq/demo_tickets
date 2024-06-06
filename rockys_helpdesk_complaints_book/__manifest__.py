{
    'name': "Rockys - Libro de reclamaciones",
    'version': '1.0',
    'depends': ['rockys_helpdesk','restful'],
    'author': "JANAQ",
    'category': '',
    'summary': 'Módulo con campos descriptivos adicionales usados por Rockys para el libro de reclamaciones',
    'description': """
    Módulo con campos descriptivos adicionales usados por Rockys para el libro de reclamaciones
    """,
    'data': [
        'data/helpdesk_team.xml',
        'data/helpdesk_ticket_type.xml',
        'data/helpdesk_ticket_channel.xml',
        'data/helpdesk_ticket_brand.xml',
        'views/helpdesk_view.xml',
        'security/ir.model.access.csv'    
    ],
}