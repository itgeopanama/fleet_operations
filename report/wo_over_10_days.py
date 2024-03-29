# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass


class WoOver10DaysXlsx(ReportXlsx):

    def get_heading(self):
        head_title = {
            'name': '',
            'rev_no': '',
            'doc_no': '',
            'image': ''
        }
        head_object = self.env['report.heading']
        head_ids = head_object.search([], order='id')
        if head_ids:
            head_rec = head_ids[0]
            if head_rec:
                head_title['name'] = head_rec.name or ''
                head_title['rev_no'] = head_rec.revision_no or ''
                head_title['doc_no'] = head_rec.document_no or ''
                head_title['image'] = head_rec.image or ''
        return head_title

    def get_wo_over_10days(self, work_orders):
        over_orders = []
        for wk_order in work_orders:
            if wk_order.state == 'done':
                diff = (datetime.strptime(wk_order.date_close,
                                          DEFAULT_SERVER_DATE_FORMAT) -
                        datetime.strptime(wk_order.date_open,
                                          DEFAULT_SERVER_DATE_FORMAT)).days
                if diff > 10:
                    over_orders.append(wk_order)
            elif wk_order.state == 'confirm':
                diff = (datetime.today() - datetime.strptime(
                    wk_order.date_open, DEFAULT_SERVER_DATE_FORMAT)).days
                if diff > 10:
                    over_orders.append(wk_order)
        return over_orders

    def get_identification(self, vehicles_id):

        ident = ""
        if vehicles_id:
            if vehicles_id.name:
                ident += vehicles_id.name or ''
            if vehicles_id.f_brand_id:
                ident += ' ' + vehicles_id.f_brand_id.name or ''
            if vehicles_id.model_id:
                ident += ' ' + vehicles_id.model_id.name or ''
        return ident

    def get_wo_status(self, status):
        wo_status = ""
        if status == 'done':
            wo_status = "Closed"
        elif status == 'confirm':
            wo_status = "Open"
        else:
            wo_status = "New"
        return wo_status

    def get_over_wo_repair_perform(self, work_order, state):
        repair_perform = ""
        status = state
        if status == "done":
            repair_perform = self.get_workperform(work_order)
        elif status == "confirm":
            repair_perform = self.get_all_selected_repair(work_order)
        return repair_perform

    def get_workperform(self, workorder_id):
        repair_type = ""
        if workorder_id:
            for repair_line in workorder_id.repair_line_ids:
                if repair_line.complete:
                    repair_type += repair_line.repair_type_id.name + ","
        return repair_type[:-1]

    def get_all_selected_repair(self, workorder_id):
        repair_type = ""
        if workorder_id:
            for repair_line in workorder_id.repair_line_ids:
                repair_type += repair_line.repair_type_id.name + ","
        return repair_type[:-1]

    def generate_xlsx_report(self, workbook, data, services):
        worksheet = workbook.add_worksheet('wo_over_10days')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 45)
        worksheet.set_column(3, 3, 10)
        worksheet.set_column(4, 4, 10)
        worksheet.set_column(5, 5, 40)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 15)
        tot = workbook.add_format({'border': 2,
                                   'font_name': 'Arial',
                                   'font_size': '12'})
        border = workbook.add_format({'border': 2,
                                      'font_name': 'Arial',
                                      'font_size': '10'})
        format1 = workbook.add_format({'border': 2,
                                       'font_name': 'Arial',
                                       'font_size': '12'})
        format1.set_bg_color('gray')
#        res = self.get_heading()
#        worksheet.merge_range('C2:D2', 'Merged Cells', merge_format)

#        file_name = res.get('image', False)
#        if file_name:
#            file1 = open('/tmp/' + 'logo.png', 'wb')
#            file_data = base64.decodestring(file_name)
#            file1.write(file_data)
#            file1.close()
        row = 0
        row += 1
#        if file_name:
#            worksheet.insert_image(row, 0, '/tmp/logo.png')
#        worksheet.write(row, 2, res['name'] or '', border)
#        worksheet.write(row, 4, 'Rev. No. :', tot)
#        worksheet.write(row, 5, res['rev_no'] or '', border)
#        worksheet.write(row, 6, 'Document No. :', tot)
#        worksheet.write(row, 7, res['doc_no'] or '', border)
        row += 1
        worksheet.write(row, 2, 'Work Order Over 10 Days', tot)
        row += 3
        res1 = self.get_wo_over_10days(services)

        worksheet.write(row, 0, 'No.', format1)
        worksheet.write(row, 1, 'WO No:', format1)
        worksheet.write(row, 2, 'Identification.', format1)
        worksheet.write(row, 3, 'Status', format1)
        worksheet.write(row, 4, 'Meter', format1)
        worksheet.write(row, 5, 'Work Performed', format1)
        worksheet.write(row, 6, 'ETIC', format1)
        row += 1
        counter = 1
        for line in res1:
            worksheet.write(row, 0, counter, border)
            worksheet.write(row, 1, line.name or '', border)
            worksheet.write(row, 2, self.get_identification(line.vehicle_id),
                            border)
            worksheet.write(row, 3, line.state, border)
            worksheet.write(row, 3, self.get_wo_status(line.state), border)
            worksheet.write(row, 4, line.odometer or 0, border)
            worksheet.write(row, 5,
                            self.get_over_wo_repair_perform(line, line.state),
                            border)
            worksheet.write(row, 6,
                            line.etic and line.date_complete or '', border)
            row += 1
            counter += 1
        row += 5


WoOver10DaysXlsx('report.wo.over.daysxls', 'fleet.vehicle.log.services')
