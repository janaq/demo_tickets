/** @odoo-module **/
import { loadJS } from "@web/core/assets";
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";

var session = require('web.session');
var core = require('web.core');
var QWeb = core.qweb;

const { format } = require('web.field_utils');
const { Component,onMounted,useExternalListener, onWillStart} = owl;

export class DashboardNPS extends Component{ 



}

DashboardNPS.template = 'DashboardNPS';
registry.category('actions').add('dashboard_nps', DashboardNPS);