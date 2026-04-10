# -*- coding: utf-8 -*-
from odoo import models, fields

class Commune(models.Model):
    _name = 'commune'
    _description = 'Commune'

    name = fields.Char(string='Nom complet', compute='_compute_name', precompute=True, store=True)
    code_postal = fields.Char(string='Code Postal', required=True)
    nom = fields.Char(string='Nom', required=True)
    code_insee = fields.Char(string='Code INSEE')
    latitude = fields.Float(string='Latitude', digits=(12, 10))
    longitude = fields.Float(string='Longitude', digits=(12, 10))
    code_departement = fields.Char(string='Code Département')
    nom_departement = fields.Char(string='Nom du Département')
    code_region = fields.Char(string='Code Région')
    nom_region = fields.Char(string='Nom de la Région')
    

    def _compute_name(self):
        for record in self:
            code = record.code_postal[:2]
            record.name = record.nom + ' (' + code + ')'
        
