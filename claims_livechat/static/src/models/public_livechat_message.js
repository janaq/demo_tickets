/** @odoo-module **/

import PublicLivechatMessage from '@im_livechat/legacy/models/public_livechat_message';

PublicLivechatMessage.include({

    /**
     * @param {@im_livechat/legacy/widgets/livechat_button} parent
     * @param {Messaging} messaging
     * @param {Object} data
     * @param {Object|Array} [data.author]
     * @param {string} [data.body = ""]
     * @param {string} [data.date] the server-format date time of the message.
     *   If not provided, use current date time for this message.
     * @param {integer} data.id
     * @param {boolean} [data.is_discussion = false]
     * @param {boolean} [data.is_notification = false]
     * @param {string} [data.message_type = undefined]
     */
     init(parent, messaging, data) {
        this._super.apply(this, arguments);
        this._is_livechat_closing_message = data.is_livechat_closing_message
    },

     /**
     * Indica si se debe realizar el cierre de la conversación
     *
     * @return {boolean}
     */
    isLivechatClosingMessage(){
        return this._is_livechat_closing_message
    },

    /**
     * Indica si se debe la configuración es la correcta
     *
     * @return {boolean}
     */
    checkConfiguration(){
        let options = this.messaging.publicLivechatGlobal.options
        let check = false
        if ( options.operator_ends_livechat && options.survey_display == 'automatic' ) { check = true }
        return check
    },

    operationLiveChat(){
        this.messaging.publicLivechatGlobal.chatWindow.widget.toggleFold(false);
        this.messaging.publicLivechatGlobal.livechatButtonView.askFeedback();
        this.messaging.publicLivechatGlobal.leaveSession();
        /* // Función _onClickClose() de PublicLivechatWindow
        if (
            this.messaging.publicLivechatGlobal.publicLivechat.unreadCounter > 0 &&
            !this.messaging.publicLivechatGlobal.publicLivechat.isFolded
        ) {
            this.messaging.publicLivechatGlobal.publicLivechat.widget.markAsRead();
        }*/
        /*// Función close() de PublicLivechatWindow
        const isComposerDisabled = this.messaging.publicLivechatGlobal.chatWindow.widget.$('.o_thread_composer input').prop('disabled');
        const shouldAskFeedback = !isComposerDisabled && this.messaging.publicLivechatGlobal.messages.find(function (message) {
            return message.id !== '_welcome';
        });
        if (shouldAskFeedback) {
            this.messaging.publicLivechatGlobal.chatWindow.widget.toggleFold(false);
            this.messaging.publicLivechatGlobal.livechatButtonView.askFeedback();
        } else {
            this.messaging.publicLivechatGlobal.livechatButtonView.closeChat();
        }
        this.messaging.publicLivechatGlobal.leaveSession();*/
    },

     /**
     * Indica si se debe la configuración es la correcta
     *
     * @return {boolean}
     */
    logoutLiveChat(){
        let options = this.messaging.publicLivechatGlobal.options
        if (this.checkConfiguration() && this.isLivechatClosingMessage()){
            let timeout = options.number_type == 's' ? options.number * 1000 : options.number
            setTimeout(this.operationLiveChat(),timeout)
        } 
        return true
    },

    /**
     * Indica si el mensaje está vacío
     *
     * @return {boolean}
     */
    isEmpty() {
        return !this._body;
    },


    /**
     * Obtenga el contenido del cuerpo de este mensaje
     *
     * @return {string}
     */
    getBody() {

        this.logoutLiveChat()
        return this._body;
    },


});