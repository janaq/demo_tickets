/** @odoo-module **/

import Feedback from '@im_livechat/legacy/widgets/feedback/feedback';
import core from 'web.core';
import session from 'web.session';
import utils from 'web.utils';
const _t = core._t;

Feedback.include({


    start() {
        let options = this.messaging.publicLivechatGlobal.options
        let head = "<span>¿Hemos respondido correctamente a tu pregunta?</span>"
        if (options.operator_ends_livechat && options.survey_display == 'automatic'){
            head = options.msg_end_livechat
        }
        // MODIFICACIÓN DE LA CABECERA
        const containers = document.querySelectorAll('.o_livechat_rating_feedback_text');
        containers.forEach(container => {
            container.innerHTML = head
        })
        // MODIFICACIÓN DEL PLACEHOLDER
        const inputs = document.getElementById('reason');
        inputs.placeholder = "Explica la razón de tu valoración"
        // MODIFICACIÓN DEL BOTÓN
        //const btns = document.querySelectorAll('.btn-primary.o_rating_submit_button')
        //btns.forEach(btn => { btn.value = "Enviar" })
        const divbuttons = document.querySelectorAll('.o_livechat_rating_reason_button')
        divbuttons.forEach(div => {
            div.innerHTML = "<button type='button' class='btn btn-primary btn-sm o_rating_submit_button' value='Enviar'>Enviar</button>"
        })

    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Object} options
     */
    _sendFeedback(reason) {
        const args = {
            uuid: this.messaging.publicLivechatGlobal.publicLivechat.uuid,
            rate: this.rating,
            reason,
        };
        this.dp.add(session.rpc('/im_livechat/feedback', args)).then((response) => {
            const emoji = this.messaging.publicLivechatGlobal.RATING_TO_EMOJI[this.rating] || "??";
            let content;
            if (!reason) {
                content = utils.sprintf(_t("Valoración: %s"), emoji);
            }
            else {
                content = "Razón de la valoración: \n" + reason;
            }
            this.trigger('send_message', { content, isFeedback: true });
        });
    },

    /**
    * @private
    */
    _showThanksMessage() {
        this.$('.o_livechat_rating_box').empty().append($('<div />', {
            text: _t('Gracias por tus comentarios'),
            class: 'text-muted'
        }));
    },

})