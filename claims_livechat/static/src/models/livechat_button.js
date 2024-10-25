/** @odoo-module **/
import LivechatButton from '@im_livechat/legacy/widgets/livechat_button';

LivechatButton.include({
    /**
     * @override
     */
    start: function () { 
        // Llamar a la implementación original
        this._super(); 
        // Nueva lógica
        //if (this.messaging.publicLivechatGlobal.options.automatically_deploy){this._onClick()}
    },

    _prepareGetSessionParameters() {
        const parameters = this._super(...arguments);
        parameters.url = window.location.pathname
        return parameters;

    }
});