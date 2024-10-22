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
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.action = useService("action");
        this.informationBrand= {};
        this.informationShop= {};
        onWillStart(async () => { 
            await loadJS("/web/static/lib/Chart/Chart.js"); // [ lib: CHART ]
            await loadJS("claims_support/static/lib/jszip.min.js"); // [ lib: ZIP ]
            await loadJS("claims_support/static/lib/FileSaver.min.js"); // [lib: saveAs ]
            this.informationShop = await this.orm.searchRead("helpdesk.tienda", [], ["id","name"])
            this.informationBrand = await this.orm.searchRead("claim.config", [], ["id","name","store_ids"])            
        })
        onMounted(()=> {
            this.informationSelectsDashboard(); // [RENDERIZAR SELECT]
            this.render_dashboards(); // [RENDERIZAR CANVAS]
            this.daterangepicker_dashboard(); // [DATERANGEPICKER]
        })
        useExternalListener(document.body, "click", (ev) => this.dowloadButtonImage(ev) );
    }




    // [ INCLUIR OPCIONES AL SELECT DE ENCUESTAS ]
    informationSelectsDashboard() {
        let self = this;
        let $options
        $.each(self.informationBrand, function( index, value ) {
            $options = $('<option/>',{text:value['name'],value:value['id']});
            $('#sltBrand').prepend($options);
        });
    }
    
    //[ RENDERIZAR TEMPLATES DE DASHBOARD ]
    render_dashboards() {}

    // [ FUNCIONALIDAD PARA EL DATERANGEPICKER ]
    daterangepicker_dashboard () {}

    // [ GRAFICAR CONSULTAS NPS EN CANVAS: FUNCIÓN PRINCIPAL ]
    async build_graphs(){}

    //[ DESCARGA DE LAS GRÁFICAS EN CANVAS ]
    downloadImages(){
    }




}

DashboardNPS.template = 'DashboardNPS';
registry.category('actions').add('dashboard_nps', DashboardNPS);