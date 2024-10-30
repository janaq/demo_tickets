/** @odoo-module **/

import Feedback from '@im_livechat/legacy/widgets/feedback/feedback';
import core from 'web.core';
import session from 'web.session';
import utils from 'web.utils';
const _t = core._t;

Feedback.include({

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