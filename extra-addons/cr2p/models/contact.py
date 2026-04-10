from odoo import models, fields, api, exceptions
from odoo.osv import expression
from collections import defaultdict


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Ajout de la sequence pour le code (IDENTIFIANT UNIQUE du contact)
    code = fields.Char(string='Code')

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        for rec in res:
            code = self.env['ir.sequence'].next_by_code('res.partner')
            rec.code = code
        return res

    create_date = fields.Datetime(string='Date de création du contact', readonly=True)
    type_contact = fields.Selection(
        string='Statut',
        selection=[
            ('inactif', 'Inactif'),
            ('prospect', 'Prospect'),
            ('actif', 'Actif'),
            ('client', 'Client'),
        ],
        default='prospect', tracking=True)

    source_contacts_parent = fields.Many2one('source_contacts', string='Source de contact', tracking=True)
    source_contacts_enfant = fields.Many2one('source_contacts.enfant', string='Source de contact', tracking=True)
    rdv_telepro = fields.Datetime(string='Date du RDV télépro', tracking=True)
    name = fields.Char(compute='_compute_name', store=True, readonly=True)
    is_company = fields.Boolean(string='Is a Company')
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice Address'),
         ('delivery', 'Delivery Address'),
         ('other', 'Other Address'),
        ], string='Address Type',
        default='other')

    # Champs pour un particulier
    align_contact = fields.Char(" ")
    civilite = fields.Selection([('m', 'M.'), ('mme', 'Mme.')], string='Civilité')
    prenom = fields.Char(string='Prénom')
    nom = fields.Char(string='Nom')
    actif_retraite = fields.Selection(string='Actif/Retraité', selection=[('actif', 'Actif'), ('retraite', 'Retraité')], default='actif')
    date_naissance = fields.Date(string='Date de naissance (01/01/1970)')
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    phone = fields.Char(string='Téléphone', readonly=True)
    email = fields.Char(string='Email', readonly=True)
    phone1 = fields.Char(string='Téléphone')
    email1 = fields.Char(string='Email')

    ajouter_contact2 = fields.Boolean(string='Ajouter une personne', default=False)
    civilite2 = fields.Selection([('m', 'M.'), ('mme', 'Mme.')], string='Civilité')
    prenom2 = fields.Char(string='Prénom')
    nom2 = fields.Char(string='Nom')
    actif_retraite2 = fields.Selection(string='Actif/Retraité', selection=[('actif', 'Actif'), ('retraite', 'Retraité')], default='actif')
    date_naissance2 = fields.Date(string='Date de naissance (01/01/1970)')
    age2 = fields.Integer(string='Age (personne 2)', compute='_compute_age2', store=True)
    phone2 = fields.Char(string='Téléphone')
    email2 = fields.Char(string='Email')

    # Champs pour une entreprise
    raison_sociale = fields.Char(string='Raison Sociale')
    forme_juridique = fields.Many2one('forme_juridique', string='Forme Juridique')
    company_registry = fields.Char(string="SIRET", size=14, readonly=False)
    vat = fields.Char(string="N° TVA", size=13, readonly=False)

    # Ajouter un correspondant pour la société
    civilite_correspondant = fields.Selection([('m', 'M.'), ('mme', 'Mme.')], string='Civilité')
    prenom_correspondant = fields.Char(string='Prénom')
    nom_correspondant = fields.Char(string='Nom')
    date_naissance_correspondant = fields.Date(string='Date de naissance (01/01/1970)')
    age_correspondant = fields.Integer(string='Age', compute='_compute_age_correspondant', store=True)
    fonction_correspondant = fields.Many2one('fonction', string='Fonction')
    telephone_correspondant = fields.Char(string='Téléphone')
    email_correspondant = fields.Char(string='Email')

    # Champs pour l'adresse principale
    is_duplicating = fields.Boolean(default=False, store=False)

    align_address = fields.Char(" ")
    rue = fields.Char(store=True)
    rue_complement = fields.Char("Rue complément", store=True)
    code_postal = fields.Char("Code postal", related="commune.code_postal", store=True, readonly=True)
    commune = fields.Many2one('commune', string="Commune", store=True)
    departement = fields.Char("Département", related="commune.nom_departement", store=True, readonly=True)

    adresse = fields.Char("Adresse", compute='_compute_address', store=True, tracking=True)
    inlined_complete_address = fields.Char(
        string="Inlined Complete Address",
        compute='_compute_complete_address', store=True, tracking=True
    )
    formatted_address = fields.Text(
        string="Formatted Address",
        compute='_compute_formatted_address', store=True, tracking=True
    )

    # Champs pour l'adresse de facturation
    duplicate_address_facturation = fields.Boolean("Duplicate Main Address for Billing", store=True, default=True)
    rue_facturation = fields.Char("Rue", inverse="_compute_facturation_address", store=True)
    rue_complement_facturation = fields.Char("Rue complément", inverse="_compute_facturation_address", store=True)
    code_postal_facturation = fields.Char("Code postal", related="commune_facturation.code_postal", inverse="_compute_facturation_address", store=True, readonly=True)
    commune_facturation = fields.Many2one('commune', string="Commune", store=True, inverse="_compute_facturation_address")
    departement_facturation = fields.Char("Département", related="commune_facturation.nom_departement", inverse="_compute_facturation_address", store=True, readonly=True)
    adresse_facturation = fields.Char("Adresse", compute='_compute_billing_address', store=True, tracking=True)
    inlined_complete_billing_address = fields.Char(
        string="Inlined Complete Billing Address",
        compute='_compute_complete_billing_address', store=True, tracking=True
    )
    formatted_billing_address = fields.Text(
        string="Formatted Billing Address",
        compute='_compute_formatted_billing_address', store=True, tracking=True
    )

    # Champs pour l'adresse de livraison
    duplicate_address_livraison = fields.Boolean("Duplicate Main Address for Delivery", store=True, default=True)
    rue_livraison = fields.Char("Rue", inverse="_compute_livraison_address", store=True)
    rue_complement_livraison = fields.Char("Rue complément", inverse="_compute_livraison_address", store=True)
    code_postal_livraison = fields.Char("Code postal", related="commune_livraison.code_postal", store=True, readonly=True)
    commune_livraison = fields.Many2one('commune', string="Commune", store=True, inverse="_compute_livraison_address")
    departement_livraison = fields.Char("Département", related="commune_livraison.nom_departement", inverse="_compute_livraison_address", store=True, readonly=True)
    adresse_livraison = fields.Char("Adresse", compute='_compute_delivery_address', store=True, tracking=True)
    inlined_complete_delivery_address = fields.Char(
        string="Inlined Complete Delivery Address",
        compute='_compute_complete_delivery_address', store=True, tracking=True
    )
    formatted_delivery_address = fields.Text(
        string="Formatted Delivery Address",
        compute='_compute_formatted_delivery_address', store=True, tracking=True
    )

    comment = fields.Html(string='Commentaires', store=True, tracking=True)

    @api.depends('is_company', 'civilite', 'nom', 'prenom', 'ajouter_contact2', 'civilite2', 'nom2', 'prenom2', 'raison_sociale', 'forme_juridique', 'nom_correspondant')
    def _compute_name(self):
        for record in self:
            if record.is_company:
                record.civilite = False
                record.prenom = False
                record.nom = False
                record.date_naissance = False
                record.age = False
                record.phone = False
                record.email = False
                record.ajouter_contact2 = False
                record.civilite2 = False
                record.prenom2 = False
                record.nom2 = False
                record.date_naissance2 = False
                record.age2 = False
                record.phone2 = False
                record.email2 = False
                record.raison_sociale = (record.raison_sociale or '').upper()
                record.nom_correspondant = (record.nom_correspondant or '').upper()
                forme_juridique = str(record.forme_juridique.name) if record.forme_juridique else ''
                parts = [forme_juridique, record.raison_sociale]

                if record.prenom_correspondant or record.nom_correspondant:
                    correspondant = f"({record.prenom_correspondant} {record.nom_correspondant})".strip()
                    parts.append(correspondant)

                record.name = ' '.join(filter(None, parts))
            else:
                record.forme_juridique = False
                record.raison_sociale = False
                record.company_registry = False
                record.vat = False
                record.civilite_correspondant = False
                record.prenom_correspondant = False
                record.nom_correspondant = False
                record.fonction_correspondant = False
                record.telephone_correspondant = False
                record.email_correspondant = False
                record.nom = (record.nom or '').upper()

                personne1 = [record.prenom or '', record.nom or '']

                if record.ajouter_contact2:
                    record.nom2 = (record.nom2 or '').upper()
                    personne2 = [record.prenom2 or '', record.nom2 or '']
                    record.name = ' et '.join([' '.join(filter(None, personne1)), ' '.join(filter(None, personne2))])
                    if record.name == ' et ':
                        record.name = False
                else:
                    record.name = ' '.join(filter(None, personne1))

        record.phone = record.phone1 or record.telephone_correspondant or ''
        record.email = record.email1 or record.email_correspondant or ''

    @api.depends('date_naissance')
    def _compute_age(self):
        for record in self:
            if record.date_naissance:
                record.age = (fields.Date.today() - record.date_naissance).days // 365

    @api.depends('date_naissance2')
    def _compute_age2(self):
        for record in self:
            if record.date_naissance2:
                record.age2 = (fields.Date.today() - record.date_naissance2).days // 365

    @api.depends('date_naissance_correspondant')
    def _compute_age_correspondant(self):
        for record in self:
            if record.date_naissance_correspondant:
                record.age_correspondant = (fields.Date.today() - record.date_naissance_correspondant).days // 365

    @api.constrains('is_company', 'company_registry')
    def _check_company_registry(self):
        for record in self:
            if record.is_company and record.company_registry:
                if len(record.company_registry) != 14 or not record.company_registry.isdigit():
                    raise exceptions.ValidationError("Le SIRET doit contenir exactement 14 chiffres.")

    @api.constrains('vat')
    def _check_vat(self, **kwargs):
        validation = kwargs.get('validation', True)
        for record in self:
            if record.vat and not re.match(r'^FR\d{11}$', record.vat):
                if validation:
                    raise exceptions.ValidationError("Le numéro de TVA doit commencer par 'FR' suivi de 11 chiffres.")
        
        if hasattr(super(ResPartner, self), '_check_vat'):
            return super(ResPartner, self)._check_vat(**kwargs)

    @api.onchange('rue', 'rue_complement', 'code_postal', 'commune', 'departement', 'duplicate_address_facturation', 'duplicate_address_livraison')
    def _onchange_main_address(self):
        if self.duplicate_address_facturation:
            self._compute_facturation_address()
        if self.duplicate_address_livraison:
            self._compute_livraison_address()

    @api.depends('rue', 'rue_complement')
    def _compute_address(self):
        for record in self:
            address_parts = [
                record.rue or '',
                record.rue_complement or ''
            ]
            record.adresse = ', '.join(filter(None, address_parts))

    @api.depends('rue', 'rue_complement', 'code_postal', 'commune', 'departement')
    def _compute_complete_address(self):
        for record in self:
            address_parts = [
                record.rue or '',
                record.rue_complement or '',
                record.code_postal or '',
                record.commune.nom or '',
                record.departement or ''
            ]
            record.inlined_complete_address = ', '.join(filter(None, address_parts))

    @api.depends('rue', 'rue_complement', 'code_postal', 'commune', 'departement')
    def _compute_formatted_address(self):
        for record in self:
            address_lines = [
                record.rue_livraison or '',
                record.rue_complement_livraison or '',
                ' '.join(filter(None, [record.code_postal or '', record.commune.nom or '', record.departement or '']))
            ]
            record.formatted_address = '\n'.join(filter(None, address_lines))

    @api.depends('duplicate_address_facturation')
    def _compute_facturation_address(self):
        for record in self:
            if record.duplicate_address_facturation:
                record.is_duplicating = False
                record.rue_facturation = record.rue or ''
                record.rue_complement_facturation = record.rue_complement or ''
                record.code_postal_facturation = record.code_postal or ''
                record.commune_facturation = record.commune or ''
                record.departement_facturation = record.departement or ''
                record.is_duplicating = True

    @api.onchange('rue_facturation', 'rue_complement_facturation', 'code_postal_facturation', 'commune_facturation', 'departement_facturation')
    def on_change_facturation(self):
        for record in self:
            record._compute_complete_billing_address()
            record._compute_formatted_billing_address()
            if not record.is_duplicating:
                if record.duplicate_address_facturation:
                    record.duplicate_address_facturation = False

    @api.depends('rue_facturation', 'rue_complement_facturation')
    def _compute_billing_address(self):
        for record in self:
            address_parts = [
                record.rue_facturation or '',
                record.rue_complement_facturation or ''
            ]
            record.adresse_facturation = ', '.join(filter(None, address_parts))

    @api.depends('rue_facturation', 'rue_complement_facturation', 'code_postal_facturation', 'commune_facturation', 'departement_facturation')
    def _compute_complete_billing_address(self):
        for record in self:
            address_parts = [
                record.rue_facturation or '',
                record.rue_complement_facturation or '',
                record.code_postal_facturation or '',
                record.commune_facturation.nom or '',
                record.departement_facturation or ''
            ]
            record.inlined_complete_billing_address = ', '.join(filter(None, address_parts))

    @api.depends('rue_facturation', 'rue_complement_facturation', 'code_postal_facturation', 'commune_facturation', 'departement_facturation')
    def _compute_formatted_billing_address(self):
        for record in self:
            address_lines = [
                record.rue_facturation or '',
                record.rue_complement_facturation or '',
                ' '.join(filter(None, [record.code_postal_facturation or '', record.commune_facturation.nom or '', record.departement_facturation or '']))
            ]
            record.formatted_billing_address = '\n'.join(filter(None, address_lines))

    @api.depends('duplicate_address_livraison')
    def _compute_livraison_address(self):
        for record in self:
            if record.duplicate_address_livraison:
                record.is_duplicating = False
                record.rue_livraison = record.rue or ''
                record.rue_complement_livraison = record.rue_complement or ''
                record.code_postal_livraison = record.code_postal or ''
                record.commune_livraison = record.commune or ''
                record.departement_livraison = record.departement or ''
                record.is_duplicating = True

    @api.onchange('rue_livraison', 'rue_complement_livraison', 'code_postal_livraison', 'commune_livraison', 'departement_livraison')
    def on_change_livraison(self):
        for record in self:
            record._compute_complete_delivery_address()
            record._compute_formatted_delivery_address()
            if not record.is_duplicating:
                if record.duplicate_address_livraison:
                    record.duplicate_address_livraison = False

    @api.depends('rue_livraison', 'rue_complement_livraison')
    def _compute_delivery_address(self):
        for record in self:
            address_parts = [
                record.rue_livraison or '',
                record.rue_complement_livraison or ''
            ]
            record.adresse_livraison = ', '.join(filter(None, address_parts))

    @api.depends('rue_livraison', 'rue_complement_livraison', 'code_postal_livraison', 'commune_livraison', 'departement_livraison')
    def _compute_complete_delivery_address(self):
        for record in self:
            address_parts = [
                record.rue_livraison or '',
                record.rue_complement_livraison or '',
                record.code_postal_livraison or '',
                record.commune_livraison.nom or '',
                record.departement_livraison or ''
            ]
            record.inlined_complete_delivery_address = ', '.join(filter(None, address_parts))

    @api.depends('rue_livraison', 'rue_complement_livraison', 'code_postal_livraison', 'commune_livraison', 'departement_livraison')
    def _compute_formatted_delivery_address(self):
        for record in self:
            address_lines = [
            record.rue_livraison or '',
            record.rue_complement_livraison or '',
            ' '.join(filter(None, [record.code_postal_livraison or '', record.commune_livraison.nom or '', record.departement_livraison or '']))
            ]
        record.formatted_delivery_address = '\n'.join(filter(None, address_lines))

    @api.model
    def _get_default_address_format(self):
        return "%(street)s\n%(street2)s\n%(zip)s %(city)s"

    def _prepare_display_address(self, without_company=False):
        address_format = self._get_address_format()
        args = defaultdict(str)
        args.update({
            'street': self.rue_facturation or '',
            'street2': self.rue_complement_facturation or '',
            'zip': self.code_postal_facturation or '',
            'city': self.commune_facturation.nom or '',
            'state_name': self.departement_facturation or '',
        })
        return address_format, args

    user_id = fields.Many2one(default=lambda self: self.env.user)

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        is_external_saleperson = self.env.user.has_group('cr2p.group_show_own_partners')
        if is_external_saleperson:
            new_domain = self.rewrite_domain_for_external_saleperson(args)
        else:
            new_domain = args
        res = super(ResPartner, self).search(new_domain, offset, limit, order)
        return res

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        is_external_saleperson = self.env.user.has_group('cr2p.group_show_own_partners')
        if is_external_saleperson:
            new_domain = self.rewrite_domain_for_external_saleperson(domain)
        else:
            new_domain = domain
        return super(ResPartner, self).web_search_read(new_domain, specification, offset, limit, order, count_limit)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        is_external_saleperson = self.env.user.has_group('cr2p.group_show_own_partners')
        if is_external_saleperson:
            new_domain = self.rewrite_domain_for_external_saleperson(domain)
        else:
            new_domain = domain
        res = super(ResPartner, self).search_read(new_domain, fields, offset, limit, order)
        return res

    @api.model
    def rewrite_domain_for_external_saleperson(self, domain):
        domain = domain if domain is not None else []
        return expression.AND([domain, ['|', ('user_id.id', '=', self.env.user.id), ('parent_id.user_id.id', '=', self.env.user.id)]])