from odoo import fields, models

class SaleReport(models.Model):
    _inherit = 'sale.report'

    second_salesperson_id = fields.Many2one(
        'res.users', 
        string="Second Salesperson", 
        readonly=True
    )
