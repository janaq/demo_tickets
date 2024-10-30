/** @odoo-module **/
import PublicLivechatView from '@im_livechat/legacy/widgets/public_livechat_view/public_livechat_view';

PublicLivechatView.include({

    events: {
        'click a': '_onClickRedirect',
        'click img': '_onClickRedirect',
        'click strong': '_onClickRedirect',
        'click .o_thread_show_more': '_onClickShowMore',
        'click .o_thread_message_needaction': '_onClickMessageNeedaction',
        'click .o_thread_message_star': '_onClickMessageStar',
        'click .o_thread_message_reply': '_onClickMessageReply',
        'click .oe_mail_expand': '_onClickMailExpand',
        'click .o_thread_message': '_onClickMessage',
        'click': '_onClick',
        'click .o_thread_message_notification_error': '_onClickMessageNotificationError',
        'click .msg_end_livechat': '_logoutLiveChat'
    },

    /**
     * @override
     */
    init(parent, messaging, options) {
        this._super.apply(this, arguments);
        this._msg_background_operator = messaging.publicLivechatGlobal.options.msg_background_operator;
        this._msg_background_public = messaging.publicLivechatGlobal.options.msg_background_public;
        this._msg_text_color_operator = messaging.publicLivechatGlobal.options.msg_text_color_operator;
        this._msg_text_color_public = messaging.publicLivechatGlobal.options.msg_text_color_public;
        this._msg_border_color_operator = messaging.publicLivechatGlobal.options.msg_border_color_operator;
        this._msg_border_color_public = messaging.publicLivechatGlobal.options.msg_border_color_public;
        this._msg_font_size = messaging.publicLivechatGlobal.options.msg_font_size;
        this._msg_font_family =  messaging.publicLivechatGlobal.options.msg_font_family
        this._allow_manual_exit = messaging.publicLivechatGlobal.options.allow_manual_exit ? 'block' : 'none'
    },
    // También puedes sobreescribir el método start() si lo deseas
    start() {
        this.$el.css('--background-operator', this._msg_background_operator);
        this.$el.css('--background-public', this._msg_background_public);
        this.$el.css('--txt-operator', this._msg_text_color_operator );
        this.$el.css('--txt-public', this._msg_text_color_public);
        this.$el.css('--border-operator', this._msg_border_color_operator );
        this.$el.css('--border-public', this._msg_border_color_public);
        this.$el.css('--font-size', this._msg_font_size);
        this.$el.css('--font-family', this._msg_font_family);
        this.$el.css('--display-close', this._allow_manual_exit);
        return this._super.apply(this, arguments);
    },

    _logoutLiveChat(){
        this.messaging.publicLivechatGlobal.chatWindow.widget.toggleFold(false);
        this.messaging.publicLivechatGlobal.livechatButtonView.askFeedback();
        this.messaging.publicLivechatGlobal.leaveSession();
    }



});