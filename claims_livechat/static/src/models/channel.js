/** @odoo-module **/

import { registerPatch } from '@mail/model/model_core';
import { attr, one } from '@mail/model/model_field';

registerPatch({
    name: 'Channel',
    fields: {
        survey_url: attr(),
        survey_id : attr(),
    },
});
