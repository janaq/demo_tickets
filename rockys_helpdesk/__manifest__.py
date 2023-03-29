{
    'name': "Rockys - HelpDesk",
    'version': '1.0',
    'depends': ['base','helpdesk'],
    'author': "JANAQ",
    'category': '',
    'summary': 'Modulo con campos descriptivos adicionales usados por Rockys',
    'description': """
    Modulo con campos descriptivos adicionales usados por Rockys
    """,
    # data files always loaded at installation
    'data': [
        #SECURITY
        'security/ir.model.access.csv',
        #VIEWS
        'views/helpdesk_views.xml',
        'views/interaccion_views.xml',
        'views/jor_views.xml',
        'views/motivo_llamada_views.xml',
        'views/soluciones_views.xml',
        'views/supervisor_views.xml',
        'views/tienda_views.xml',
   ],
    # data files containing optionally loaded demonstration data
    #'demo': [
    #    'demo/demo_data.xml',
    #],
}