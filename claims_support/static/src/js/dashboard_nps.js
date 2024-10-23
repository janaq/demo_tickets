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
            this.informationBrand = await this.orm.searchRead("claim.config", [], ["id","name","store_ids"]) 
            this.informationShop = await this.orm.searchRead("helpdesk.tienda", [], ["id","name"])
                       
        })
        onMounted(()=> {
            this.informationSelectsDashboard(); // [RENDERIZAR SELECT]
            this.daterangepickerDashboard(); // [DATERANGEPICKER]
            this.renderDashboard(); // [RENDERIZAR CANVAS]
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
        $.each(self.informationShop, function( index, value ) {
            $options = $('<option/>',{text:value['name'],value:value['id']});
            $('#sltShop').prepend($options);
        });
    }

    // [ FUNCIONALIDAD PARA EL DATERANGEPICKER ]
    daterangepickerDashboard () {
        $(function() {
            let start = moment().subtract(6, 'days');
            let end = moment();
            function cb(start, end) {
                $('#divRange span').html(start.format('D MMMM, YYYY') + ' - ' + end.format('D MMMM, YYYY'));
                $("#divRange").prop("rangeStart",start.format('YYYY-MM-DD'));
                $("#divRange").prop("rangEnd",end.format('YYYY-MM-DD'));
                $('#statistics').click()
            }
            $('#divRange').daterangepicker({
                startDate: start,
                endDate: end,
                ranges: {
                    'Hoy': [moment(), moment()],
                    'Ayer': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                    'Últimos 7 días': [moment().subtract(6, 'days'), moment()],
                    'Últimos 30 días': [moment().subtract(29, 'days'), moment()],
                    'Este mes': [moment().startOf('month'), moment().endOf('month')],
                    'Mes pasado': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
                }
            }, cb);
            cb(start, end);
        });
    }
    
    //[ RENDERIZAR TEMPLATES DE DASHBOARD ]
    renderDashboard() {
        let self = this;
        let tmps = ['NetPromoterScore','SurveyParticipation','NPSBreakdown','NPSValue'];
        let tmps_1 = ['NPStore'];
        _.each(tmps, function(tmp) { $('.o_hr_dashboard').append(QWeb.render(tmp, {widget: self})); });
        _.each(tmps_1, function(tmp) { $('.o_hr_dashboard_general').append(QWeb.render(tmp, {widget: self})); });
    }

    // [ GRAFICAR CONSULTAS NPS EN CANVAS: FUNCIÓN PRINCIPAL ]
    async buildGraphs(){
        console.log('OPERACIONES PARA LA VISUALIZACIÓN DE LOS CÁLCULOS')
    }

    // [ DESCARGA GRUPAL DE LAS GRÁFICAS EN FORMATO ZIP ]
    downloadImages(){
        let zip = new JSZip();
        let d = new Date();
        zip.file("NPS SCORE NETO - "+d+".png", graphScoreNeto.toBase64Image().replace('data:image/png;base64,',''), {base64: true});
        zip.file("PARTICIPACIÓN EN LAS ENCUESTAS - "+d+".png", graphSurveyParticipation.toBase64Image().replace('data:image/png;base64,',''), {base64: true});
        zip.file("NPS BREAKDOWN - "+d+".png", graphBreakdown.toBase64Image().replace('data:image/png;base64,',''), {base64: true});
        zip.file("NPS VALUE - "+d+".png", graphValue.toBase64Image().replace('data:image/png;base64,',''), {base64: true});
        zip.file("NPS STORE - "+d+".png", graphStore.toBase64Image().replace('data:image/png;base64,',''), {base64: true});
        zip.generateAsync({type:"blob"}).then(function(content) {   saveAs(content, "Dashboard NPS "+d+".zip"); });
    }
    // [ DESCARGA INDIVIDUAL EN FORMATO PNG ]
    dowloadButtonImage(ev){
        let self = this
        if (ev.target.id == 'downloadBtnNetPromoterScore'){ self.downloadBtnNetPromoterScore() }
        if (ev.target.id == 'downloadBtnSurveyParticipation') { self.downloadBtnSurveyParticipation() }
        if (ev.target.id == 'downloadBtnNPSBreakdown') { self.downloadBtnNPSBreakdown() }
        if (ev.target.id == 'downloadBtnNPSValue') { self.downloadBtnNPSValue()}
        if (ev.target.id == 'downloadBtnNPStore') { self.downloadBtnNPStore()}

    }
    downloadBtnNetPromoterScore(){
        let d = new Date();
        let a = document.createElement('a');
        a.href = graphScoreNeto.toBase64Image();
        a.download = 'NPS SCORE NETO '+ d +'.png' ;
        a.click();
    }
    downloadBtnSurveyParticipation(){
        let d = new Date();
        let a = document.createElement('a');
        a.href = graphSurveyParticipation.toBase64Image();
        a.download = 'PARTICIPACIÓN EN LAS ENCUESTAS '+ d +'.png' ;
        a.click();
    }
    downloadBtnNPSBreakdown(){
        let d = new Date();
        let a = document.createElement('a');
        a.href = graphBreakdown.toBase64Image();
        a.download = 'NPS BREAKDOWN '+ d +'.png' ;
        a.click();
    }
    downloadBtnNPSValue(){
        let d = new Date();
        let a = document.createElement('a');
        a.href = graphValue.toBase64Image();
        a.download = 'NPS VALUE '+ d +'.png' ;
        a.click();
    }
    downloadBtnNPStore(){
        let d = new Date();
        let a = document.createElement('a');
        a.href = graphStore.toBase64Image();
        a.download = 'NPS VALUE '+ d +'.png' ;
        a.click();
    }

}

DashboardNPS.template = 'DashboardNPS';
registry.category('actions').add('dashboard_nps', DashboardNPS);