/** @odoo-module **/

import PublicLivechatWindow from '@im_livechat/legacy/widgets/public_livechat_window/public_livechat_window';

PublicLivechatWindow.include({
    init(parent, messaging, thread) {
        this._super.apply(this, arguments);
        this._msg_background_operator = messaging.publicLivechatGlobal.options.msg_background_operator;
        this._msg_background_public = messaging.publicLivechatGlobal.options.msg_background_public;
        this._msg_text_color_operator = messaging.publicLivechatGlobal.options.msg_text_color_operator;
        this._msg_text_color_public = messaging.publicLivechatGlobal.options.msg_text_color_public;
        this._msg_border_color_operator = messaging.publicLivechatGlobal.options.msg_border_color_operator;
        this._msg_border_color_public = messaging.publicLivechatGlobal.options.msg_border_color_public;
        this._msg_font_size = messaging.publicLivechatGlobal.options.msg_font_size;
        this._msg_font_family =  messaging.publicLivechatGlobal.options.msg_font_family    
    },
    
    async start() {
        this.$el.css('--background-operator', this._msg_background_operator);
        this.$el.css('--background-public', this._msg_background_public);
        this.$el.css('--txt-operator', this._msg_text_color_operator );
        this.$el.css('--txt-public', this._msg_text_color_public);
        this.$el.css('--border-operator', this._msg_border_color_operator );
        this.$el.css('--border-public', this._msg_border_color_public);
        this.$el.css('--font-size', this._msg_font_size);
        this.$el.css('--font-family', this._msg_font_family);
        return this._super.apply(this, arguments);
    }
});