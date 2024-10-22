/** @odoo-module **/
import PublicLivechatView from '@im_livechat/legacy/widgets/public_livechat_view/public_livechat_view';

PublicLivechatView.include({
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
    },
    // También puedes sobreescribir el método start() si lo deseas
    start() {
        this.$el.css('--background-operator', this._msg_background_operator);
        this.$el.css('--background-public', this._msg_background_public);
        this.$el.css('--txt-operator', this._msg_text_color_operator );
        this.$el.css('--txt-public', this._msg_text_color_public);
        this.$el.css('--border-operator', this._msg_border_color_operator );
        this.$el.css('--border-public', this._msg_border_color_public);
        return this._super.apply(this, arguments);
    }
});