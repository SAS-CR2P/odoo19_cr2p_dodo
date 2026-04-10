from odoo import models, fields, api, exceptions

class ResUser(models.Model):
    _inherit = 'res.users'

    name = fields.Char(compute='_compute_name', store=True, readonly=True)
    
    civilite = fields.Selection([('m', 'M.'), ('mme', 'Mme.')], string='Civilité')
    prenom = fields.Char(string='Prénom')
    nom = fields.Char(string='Nom')
    date_naissance = fields.Date(string='Date de naissance')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    phone = fields.Char(string='Téléphone')
    login = fields.Char(string='Identifiant')
    email = fields.Char(string='Email')

    date_debut_service = fields.Date(string='Date de début de service')
    date_fin_service = fields.Date(string='Date de fin de service')

    # Compute NOM Prénom
    @api.depends('name', 'prenom', 'nom')
    @api.onchange('prenom', 'nom')
    def _compute_name(self):
        for record in self:
            record.nom = (record.nom or '').upper()
            utilisateur = [record.prenom or '', record.nom or '']
            record.name = ' '.join(filter(None, utilisateur))

    @api.depends('login', 'email')
    def _change_login_email(self):
        for record in self:
            record.email = record.login
    
    # Calcul de l'âge
    @api.depends('date_naissance')
    def _compute_age(self):
        for record in self:
            if record.date_naissance:
                record.age = (fields.Date.today() - record.date_naissance).days // 365