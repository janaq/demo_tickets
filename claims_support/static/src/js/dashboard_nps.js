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
        let self = this
        let rangeStart = $('#divRange').prop('rangeStart')
        let rangEnd = $('#divRange').prop('rangEnd')
        let brand = parseInt($('#sltBrand').val())
        let shop = parseInt($('#sltShop').val())
        let tmp = $('#select-time-filter').val()
        const info = await this.rpc(  '/data_dashboardNPS', { rangeStart: rangeStart, rangEnd: rangEnd, brand: brand, shop: shop, tmp:tmp});
        const plugin = {
            id: 'custom_canvas_background_color',
            beforeDraw: (chart) => {
                const ctx = chart.canvas.getContext('2d');
                ctx.save();
                ctx.globalCompositeOperation = 'destination-over';
                ctx.fillStyle = 'White';
                ctx.fillRect(0, 0, chart.width, chart.height);
                ctx.restore();
            }
        };
        if (info){
            // GENERAL
            let general = info.general
            if (!general.legend){
                $(".legend").addClass("legend-none");
            } else {
                $(".legend").removeClass("legend-none");
            }
            // PARTICIPACIÓN EN LA ENCUESTA
            let participationSurvey = info.participationSurvey
            let ctxParticipationSurvey = document.getElementById('SurveyParticipation').getContext('2d');
            if (window.graphSurveyParticipation) {
                window.graphSurveyParticipation.clear();
                window.graphSurveyParticipation.destroy();
            }
            window.graphSurveyParticipation = new Chart(ctxParticipationSurvey, {
                data: {
                    datasets: [{
                        type: 'bar',
                        label: 'Número de participaciones',
                        data: participationSurvey.values,
                        backgroundColor: ['rgba(255, 99, 132, 0.2)'],
                        borderColor: ['rgba(255, 99, 132, 1)'],
                        borderWidth: 1,
                        stack: 1
                    }],
                    labels: participationSurvey.fields
                },
                plugins: [plugin],
                options: { scales: {    xAxes: [{ id: 'y', display: true, title: { display: true, text: 'value' } }],
                                        yAxes: [{ id: 'y', display: true, title: { display: true, text: 'value' } }]
                }},
            });
            // NPS SCORE NETO = % PROMOTORES - % DETRACTORES
            let netPromoterScore = info.netPromoterScore
            let ctxNetPromoterScore = document.getElementById('NetPromoterScore').getContext('2d');
            if (window.graphScoreNeto) {
                window.graphScoreNeto.clear();
                window.graphScoreNeto.destroy();
            }
            window.graphScoreNeto = new Chart(ctxNetPromoterScore, {
                type: 'line',
                data: {
                    labels: netPromoterScore.fields,
                    datasets: [{
                        label: 'NPS Score(%)',
                        data: netPromoterScore.values,
                        fill: false,
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                },
                plugins: [plugin],
                options: { scales: {    xAxes: [{ id: 'y', display: true, title: { display: true, text: 'value' } }],
                                        yAxes: [{ id: 'y', display: true, title: { display: true, text: 'value' } }]
                }},
            });
            // NPS VALUE
            let valueSurvey = info.valueSurvey
            let ctxvalueSurvey = document.getElementById('NPSValue').getContext('2d');
            if (window.graphValue) {
                window.graphValue.clear();
                window.graphValue.destroy();
            }
            window.graphValue = new Chart(ctxvalueSurvey, {
                type: 'bar',
                data: {
                    labels: valueSurvey.fields,
                    datasets: [{
                        label: 'Respuestas (%)',
                        data: valueSurvey.values,
                        backgroundColor: ['rgba(153, 102, 255, 0.2)'],
                        borderColor: ['rgba(153, 102, 255, 1)'],
                        borderWidth: 1
                    }]
                },
                plugins: [plugin],
                options: { scales: {    xAxes: [{ id: 'y', display: true, title: { display: true, text: 'value' } }],
                                        yAxes: [{ id: 'y', display: true, title: { display: true, text: 'value' } }]
                }},
            });
            // NPS BREAKDOWN
            let breakdownSurvey = info.breakdownSurvey
            let ctxBreakdownSurvey = document.getElementById('NPSBreakdown').getContext('2d');
            if (window.graphBreakdown) {
                window.graphBreakdown.clear();
                window.graphBreakdown.destroy();
            }
            window.graphBreakdown = new Chart(ctxBreakdownSurvey, {
                data: {
                    datasets: [{
                        type: 'line',
                        label: 'Promotores(%)',
                        data: breakdownSurvey.valuesProm,
                        fill: false,
                        borderColor: 'rgb(40, 180, 99)',
                        stack: 1
                    }, {
                        type: 'line',
                        label: 'Neutros(%)',
                        data: breakdownSurvey.valuesNeut,
                        fill: false,
                        borderColor: 'rgba(244, 208, 63)',
                        stack: 2
                    },{
                        type: 'line',
                        label: 'Detractores(%)',
                        data: breakdownSurvey.valuesDetr,
                        fill: false,
                        borderColor: 'rgb(192, 57, 43)',
                        stack: 3
                    }],
                    labels: breakdownSurvey.fields
                },
                plugins: [plugin],
                options: { scales: {    xAxes: [{ id: 'y', display: true, title: { display: true, text: 'value' } }],
                                        yAxes: [{ id: 'y', display: true, title: { display: true, text: 'value' } }]
                }},
            });    
            // NPS POR TIENDA
            let shopSurvey = info.shopSurvey
            let ctxShopSurvey = document.getElementById('NPStore').getContext('2d');
            if (window.graphStore) {
                window.graphStore.clear();
                window.graphStore.destroy();
            }
            window.graphStore = new Chart(ctxShopSurvey, {
                data: {
                    datasets: [ {
                        type: 'line',
                        label: 'NPS Score(%)',
                        data: shopSurvey.valuesPromoterSCore,
                        fill: false,
                        borderColor: 'rgb(75, 192, 192)',
                        stack: 2
                    },
                    {
                        type: 'bar',
                        label: 'Número de participaciones',
                        data: shopSurvey.valuesParticipation,
                        backgroundColor: ['rgba(255, 99, 132, 0.2)'],
                        borderColor: ['rgba(255, 99, 132, 1)'],
                        borderWidth: 1,
                        stack: 1
                    },],
                    labels: shopSurvey.fieldsParticipation
                },
                plugins: [plugin],
                options: { scales: {    xAxes: [{ id: 'y', display: true, title: { display: true, text: 'value' } }],
                                        yAxes: [{ id: 'y', display: true, title: { display: true, text: 'value' } }]
                }},
            });





        }
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