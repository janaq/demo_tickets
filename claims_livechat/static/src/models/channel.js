/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr, one } from '@mail/model/model_field';

registerPatch({
    name: 'Channel',
    fields: {
        survey_url: attr(),
        survey_id : attr(),
        livechat_active: attr(),
        operator_ends_livechat: attr(),
        msg_end_livechat: attr()
    },
});
