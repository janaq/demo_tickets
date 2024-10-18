/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';
import { ChatWindowHeader } from '@mail/components/chat_window_header/chat_window_header';

export class ExtendedChatWindowHeader extends ChatWindowHeader {
    
    get GoToTheSurvey() {
        console.log('NUeva información',this.props.chatWindow.thread.channel.__values['survey_id'])
        return true;
    }
}

Object.assign(ExtendedChatWindowHeader, {
    props: {
        chatWindow: Object,
        record: Object,
    },
    template: 'mail.ChatWindowHeader',
});
registerMessagingComponent(ExtendedChatWindowHeader);