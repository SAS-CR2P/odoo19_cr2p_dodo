# -*- coding: utf-8 -*-
from odoo import models, fields, api
import urllib.parse

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    name = fields.Char(compute='_compute_name', readonly=True)
    liste_titre = fields.Selection([('rdv', 'Rendez-vous'), ('réunion', 'Réunion'), ('perso', 'Perso'), ('autre', 'Autre')], default="rdv", string='Type de rendez-vous')
    titre = fields.Char('Titre')
    contact = fields.One2many('res.partner', string='Contact')

    partner_ids = fields.Many2many('res.partner', string='Participant(s)',
        domain=lambda self: [('id', 'in', self._get_user_partner_ids())]
    )

    contact = fields.Many2one(
        'res.partner', 
        string='Contact',
        domain=lambda self: [('id', 'not in', self._get_user_partner_ids())]
    )

    def _get_user_partner_ids(self):
        # Récupérer tous les partner_ids des utilisateurs
        return self.env['res.users'].search([]).mapped('partner_id').ids


    emplacement = fields.Selection([('domicile client', 'Domicile client'), ('agence dax', 'Agence Dax'), ('agence cestas', 'Agence Cestas'), ('autre', 'Autre')], string='Emplacement')
    adresse = fields.Text('Adresse', inverse='_inverse_adresse') #multiline?
    url_waze = fields.Char(string='Itinéraire Waze', readonly=True)

    @api.onchange('partner_ids', 'emplacement', 'adresse')
    def _inverse_adresse(self):
        if self.emplacement == 'domicile client':
            if self.contact:
                formatted_address = self.contact.formatted_address

                base_url = "waze://?q="
                adresse_encodee = urllib.parse.quote(formatted_address or "") 
                self.url_waze = f"{base_url}{adresse_encodee}"
            else:
                self.url_waze = ""
            self.adresse = formatted_address or "" 
        elif self.emplacement == 'agence dax':
            self.adresse = "547 Rue Bernard Palissy, 40990 Saint-Paul-lès-Dax"
        elif self.emplacement == 'agence cestas':
            self.adresse = "57 Avenue Maréchal de Lattre de Tassigny, 33610 Cestas"
        elif self.emplacement == 'autre':
            self.adresse = "Autre"

    @api.depends('liste_titre', 'titre', 'partner_ids', "contact")
    def _compute_name(self):
        for record in self:
            if record.liste_titre == False:
                record.name = f"{record.titre or ''}"
            elif record.liste_titre == 'rdv':
                if record.contact: 
                    record.name = f"RDV avec {record.contact.name  or ''}"
                else:
                    record.name = f"RDV {record.titre or ''}"
            elif record.liste_titre == 'réunion':
                record.name = f"Réu. {record.titre or ''}"
            elif record.liste_titre == 'perso':
                record.name = "Perso."
            elif record.liste_titre == 'autre':
                record.name = f"{record.titre or ''}"