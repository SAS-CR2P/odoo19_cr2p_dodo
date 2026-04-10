# -*- coding: utf-8 -*-
from odoo import models, fields

class PartnerFonction(models.Model):
    _name = 'fonction'
    _order = 'name'
    _description = 'Fonction'

    name = fields.Char(string='Fonction', required=True)