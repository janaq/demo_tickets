{
    'name': "LiveChat: Soporte de reclamaciones",
    'version': '1.0',
    'depends': ['base','claims_support','im_livechat','mail'],
    'installable': True,
    'author': "JANAQ",
    'category': '',
    'summary': 'Módulo para la integración de LiveChat y el Soporte de reclamaciones',
    'description': """""",
    'data': [
        'views/res_config_settings_views.xml',
        'views/claims_support_views.xml',
        'views/im_livechat_channel_templates.xml',
        'views/mail_channel_views.xml',
        'views/nps_survey_views.xml',
    ],
    'assets': {
        'mail.assets_messaging': [
            'claims_livechat/static/src/models/channel.js',
        ],
        'mail.assets_discuss_public': [
            # Dependency of notification_group, notification_request, thread_needaction_preview and thread_preview
            #'claims_livechat/static/src/components/*/*',    
        ],
        'web.assets_frontend': [
            ('include', 'im_livechat.assets_public_livechat'),
            'claims_livechat/static/src/components/*/*.scss',
        ],
        'im_livechat.external_lib': [
            'claims_livechat/static/src/components/*/*.scss',
        ],
        'web.assets_backend': [
            # defines mixins and variables used by multiple components
            'claims_livechat/static/src/components/*/*.xml',
        ],
        'im_livechat.assets_public_livechat': [
            ('include', 'mail.assets_core_messaging'),
            'claims_livechat/static/src/models/public_livechat_view.js',
            'claims_livechat/static/src/models/livechat_button.js',
            'claims_livechat/static/src/models/public_livechat_window.js',
        ],
    },
}