# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime , timedelta , date
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api 
from openerp import tools
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools.translate import _
import re
import logging

_logger = logging.getLogger(__name__) 



class ba_hr_loan_application(models.Model):

    _name = 'ba.hr.loan.application'
    _description = "Pedido de prestamo"

    _inherit = ['mail.thread']

    state = fields.Selection([('request','Solicitado'),
                            ('gestion','En Gestion'),('deny','Denegado'),('apply','Aprobado'),('close','Finalizado')],
                            track_visibility='onchange' , default = 'request' )

    user_id = fields.Many2one('res.users', required=True) 

    name = fields.Many2one('hr.employee' ,compute="_compute_employee") 

    date = fields.Date('Fecha', default=date.today() , required=True) 
    antiquity = fields.Char('antigüedad' ,compute="_compute_antiquity" , required=True) 

    causa = fields.Selection([('Salud','Salud'),('Financiero','Financiero'),('Alquiler','Alquiler')],
                            string="Motivo de la Solicitud", required=True)
    reason = fields.Text('Razon de la Solicitud', required=True)
    emp_sanctions=fields.Boolean('¿Has tenido sanciones los últimos 3 Meses?') 
    emp_assistance=fields.Boolean('¿Has tenido el 90% de presentismo los últimos 3 Meses?') 

    emp_credit = fields.Boolean('¿Ténes descuentos por crédito Magenta?') 
    emp_seizure = fields.Boolean('¿Ténes descuentos por embargo comercial?') 

    amount = fields.Selection([('5000','5000'),('3000','3000')],
                            string="Monto solicitado", required=True)
    
    magenta_credit = fields.Many2one('magenta.ayuda','Credito') 



    @api.multi
    @api.depends('user_id')
    def _compute_employee(self):
        for loan in self: 
            if loan.user_id :
                employee_id = self.env['hr.employee'].search([('user_id','=',loan.user_id.id)])
                if employee_id:
                    loan.name = employee_id[0]


    @api.depends('date','name')
    def _compute_antiquity(self):
        diff = relativedelta(fields.Date.from_string(self.date) , fields.Date.from_string(self.name.admision_date)).years
        self.antiquity = "%d años" % diff


    @api.model
    def create(self,vals) :
        vals['message_follower_ids'] = []

        blancoamor_credito = self.env['ir.model.data'].get_object( 'magenta', 'blancoamor_credito')

        #blancoamor_credito = self.env['ir.model.data'].get_object( 'ba_conf', 'blancoamor_credito')
        rec = super(ba_hr_loan_application, self).create(vals)   
        return rec        

    @api.one
    def deny(self):
        self.write({'state':'deny'})

    @api.one
    def apply(self):
        self.write({'state':'apply'})

    @api.one
    def gestion(self):
        self.write({'state':'gestion'})