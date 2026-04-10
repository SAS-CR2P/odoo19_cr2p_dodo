# -*- coding: utf-8 -*-
from odoo import models, fields

class PartnerSourceContacts(models.Model):
    _name = 'source_contacts'
    _order = 'name'
    _description = 'Source de contacts'

    name = fields.Char(string='Source', required=True)
    enfant = fields.Boolean(string='''L'élément a plusieurs enfants''', default=False)

class PartnerSourceContactsEnfant(models.Model):
    _name = 'source_contacts.enfant'
    _description = 'Source de contacts enfants'

    name = fields.Char(string='Source', required=True)
    parent = fields.Many2one('source_contacts', string='Parent')

