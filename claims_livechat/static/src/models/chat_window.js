/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';

registerPatch({
    name: 'ChatWindow',
    recordMethods: {
        /**
         * @param {MouseEvent} ev
         */
        async onClickLogoutLiveChat(ev) {
            ev.stopPropagation();
            if (this.thread.channel.livechat_active) {
                const resolution = await this.messaging.rpc({
                    route: "/im_livechat/msg_operator_logout",
                    params: { channel_id: this.thread.channel.id },
                });
                if (resolution && resolution.type === 'ir.actions.act_window'){ 
                    resolution['views'] = [[false, 'form']]
                    
                    this.env.services.action.doAction(resolution) 
                }
            }
        },
    },
});
