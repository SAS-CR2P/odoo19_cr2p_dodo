# -*- coding: utf-8 -*-
from odoo import fields, models


class CrmLeadProductType(models.Model):
    _name = 'crm.lead.product.type'
    _description = 'Type de produit CRM'
    _order = 'sequence, id'

    name = fields.Char(string='Nom', required=True)
    code = fields.Char(string='Code', required=True)
    color = fields.Integer(string='Couleur')
    sequence = fields.Integer(string='Séquence', default=10)
    active = fields.Boolean(default=True)
