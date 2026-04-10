# -*- coding: utf-8 -*-
from odoo import models, fields

class FormeJuridique(models.Model):
    _name = 'forme_juridique'
    _description = 'Forme Juridique'

    name = fields.Char(string='Forme juridique', required=True)