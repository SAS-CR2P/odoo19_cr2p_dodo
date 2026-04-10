from odoo import models, fields, api, _
import base64

from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = "sale.order"

    second_salesperson_id = fields.Many2one('res.users', string='Deuxième vendeur')

    total_discount = fields.Float(string='Total Discount', compute='_compute_total_discount')
    total_discount_percent = fields.Float(string='Total Discount (%)', compute='_compute_total_discount')

    is_discount_degradation = fields.Boolean(string='Is Discount Degradation', compute='_compute_discount')
    is_high_discount = fields.Boolean(string='Is High Discount', compute='_compute_discount')

    discount_normal_max = fields.Float(string="Remise standard", compute="_get_discount_and_warning", readonly=True, store=True)
    discount_max_allowed = fields.Float(string="Remise maximum autorisée", compute="_get_discount_and_warning", readonly=True, store=True)
    discount_warning_message = fields.Char(string="Message d'avertissement en cas de dépassement de la remise standard", compute="_get_discount_and_warning", readonly=True, store=True)
    discount_max_warning_message = fields.Char(string="Message d'avertissement en cas de dépassement de la remise maximum autorisée", compute="_get_discount_and_warning", readonly=True, store=True)

    @api.onchange('total_discount', 'amount_total', 'order_line')
    @api.depends('total_discount', 'amount_total', 'order_line')
    def _get_discount_and_warning(self):
        for record in self:
            # Récupérer les valeurs des paramètres de configuration
            record.discount_normal_max = float(self.env['ir.config_parameter'].sudo().get_param('sale.discount_normal_max'))
            record.discount_max_allowed = float(self.env['ir.config_parameter'].sudo().get_param('sale.discount_max_allowed'))
            record.discount_warning_message = self.env['ir.config_parameter'].sudo().get_param('sale.discount_warning_message')
            record.discount_max_warning_message = self.env['ir.config_parameter'].sudo().get_param('sale.discount_max_warning_message')

    @api.onchange('total_discount', 'amount_total', 'order_line')
    @api.depends('total_discount', 'amount_total', 'order_line')
    def _compute_discount(self):
        for record in self:
            record.is_discount_degradation = True if record.total_discount > (record.amount_total * (record.discount_normal_max / 100)) else False
            record.is_high_discount = True if record.total_discount > (record.amount_total * (record.discount_max_allowed / 100)) else False

    @api.depends('order_line.price_total', 'order_line.discount', 'order_line.product_uom_qty')
    def _compute_total_discount(self):
        for order in self:
            line_discounts = sum(line.price_unit * line.discount * line.product_uom_qty / 100 for line in order.order_line if line.discount > 0)
            global_discounts = sum(line.price_total for line in order.order_line if line.price_total < 0)
            order.total_discount = line_discounts + abs(global_discounts)
            order.total_discount_percent = (order.total_discount / order.amount_total) if order.amount_total else 0


    @api.constrains('order_line')
    def _check_discount(self):
        for order in self:
            # Récupérer les valeurs des paramètres de configuration
            order.discount_normal_max = float(self.env['ir.config_parameter'].sudo().get_param('sale.discount_normal_max'))
            order.discount_max_allowed = float(self.env['ir.config_parameter'].sudo().get_param('sale.discount_max_allowed'))
            order.discount_warning_message = self.env['ir.config_parameter'].sudo().get_param('sale.discount_warning_message')
            order.discount_max_warning_message = self.env['ir.config_parameter'].sudo().get_param('sale.discount_max_warning_message')

            if order.is_high_discount:
                raise ValidationError(_("%s. Réévaluer la remise totale à moins de %s %%") % (order.discount_max_warning_message, order.discount_max_allowed))


    def action_confirm(self):
        # Vérifiez ici vos conditions personnalisées
        # Exemple : empêcher la confirmation si le champ `discount_warning_display` est rempli
        for order in self:
            if order.is_high_discount:
                # Empêcher la confirmation et afficher un message d'avertissement
                raise UserError(_('La confirmation du devis est empêchée en raison du dépassement de la remise, pour rappel la valeur totale de la remise est de : %s' % order.discount_max_allowed))

        # Appeler la méthode originale si les conditions sont remplies
        return super(SaleOrder, self).action_confirm()

    # === CHAMPS DATES LIVRAISON ===#
    date_souhait_client_livraison = fields.Date("Date de livraison souhaitée par le client")

    def _get_default_date_limite_livraison(self):
        return fields.Date.today() + relativedelta(months=+6)

    date_limite_livraison = fields.Date(
        "Date limite de livraison",
        default=_get_default_date_limite_livraison,
    )

    # === CHAMPS COMPTANT ===#
    
    choix_acompte = fields.Selection(
        [
            ("pourcentage", "%"),
            ("euros", "€"),
        ],
        default="pourcentage"
    )

    acompte_commande_pourcentage = fields.Float("Acompte à la commande (%)", default=30)
    acompte_commande_montant = fields.Float("Montant de l'acompte (€)", default=0)
    solde_fin_chantier = fields.Float("Solde à régler en fin de chantier (€)", readonly=True, compute='_compute_solde_fin_chantier')
    payable_en = fields.Integer("Payable en (fois)", default=1)

    
    @api.depends('amount_total', 'choix_acompte', 'acompte_commande_pourcentage', 'acompte_commande_montant')
    def _compute_solde_fin_chantier(self):
        for order in self:
            if order.choix_acompte == 'pourcentage':
                order.acompte_commande_montant = order.amount_total * (order.acompte_commande_pourcentage / 100.0)
            elif order.choix_acompte == 'euros':
                order.acompte_commande_pourcentage = (order.acompte_commande_montant / order.amount_total) * 100 if order.amount_total else 0

            order.solde_fin_chantier = order.amount_total - order.acompte_commande_montant
    

    # === CHAMPS FINANCEMENT ===#
    versement_commande = fields.Float("Versement à la commande (€)")
    versement_pose = fields.Float("Versement à la pose (€)")
    montant_financement = fields.Float("Montant du financement (€)")
    duree_financement = fields.Integer("Durée du financement (mois)")
    nombre_mensualites = fields.Integer("Nombre de mensualités")
    montant_mensualites_sans_assurance = fields.Float(
        "Montant des mensualités sans assurance (€)"
    )
    montant_mensualites_avec_assurance = fields.Float(
        "Montant des mensualités avec assurance (€)"
    )
    taux_annuel_nominal = fields.Float("Taux annuel nominal (%)")
    taux_annuel_effectif_global = fields.Float("Taux annuel effectif global (%)")

    is_financing_payment_term = fields.Boolean(
        string="Is Financing Payment Term",
        compute="_compute_is_financing_payment_term",
        store=True,  # Optionnel, selon le besoin
    )

    # is_mixte_payment_term = fields.Boolean(
    #     string="Is Mixte Payment Term",
    #     compute="_compute_is_mixte_payment_term",
    #     store=True,  # Optionnel, selon le besoin
    # )

    financement_ok = fields.Boolean(
        string="Financement OK",
        compute="_compute_financement_ok",
        store=True,  # Optionnel, selon le besoin
    )

    @api.depends("payment_term_id")
    def _compute_is_financing_payment_term(self):
        financing_terms = [
            "account_payment_term_financement_cetelem",
            "account_payment_term_financement_sofinco",
            "account_payment_term_financement_domofinance",
            "account_payment_term_mixte_financement_cetelem",
            "account_payment_term_mixte_financement_domofinance",
            "account_payment_term_mixte_financement_sofinco",
        ]
        # mixte_terms = [
        #     "account_payment_term_mixte_financement_cetelem",
        #     "account_payment_term_mixte_financement_domofinance",
        #     "account_payment_term_mixte_financement_sofinco",
        # ]

        for record in self:
             # Obtenez l'identifiant technique (external ID) de payment_term_id
            external_id = self.env['ir.model.data'].search([
                ('model', '=', 'account.payment.term'),
                ('res_id', '=', record.payment_term_id.id)
            ]).name

            # Comparez l'identifiant technique avec votre liste
            record.is_financing_payment_term = external_id in financing_terms

            if not record.is_financing_payment_term:
                record.versement_commande = False
                record.versement_pose = False
                record.montant_financement = False
                record.duree_financement = False
                record.nombre_mensualites = False
                record.montant_mensualites_sans_assurance = False
                record.montant_mensualites_avec_assurance = False
                record.taux_annuel_nominal = False
                record.taux_annuel_effectif_global = False

            if record.is_financing_payment_term:
                record.acompte_commande_pourcentage = False
                record.acompte_commande_montant = False
                record.solde_fin_chantier = False
                record.payable_en = False

            # record.is_mixte_payment_term = external_id in mixte_terms


    @api.depends("payment_term_id", "is_financing_payment_term", "amount_total", "versement_commande", "versement_pose", "montant_financement")
    @api.onchange("payment_term_id", "is_financing_payment_term", "amount_total", "versement_commande", "versement_pose", "montant_financement")
    def _compute_financement_ok(self):
        for record in self:
            if record.is_financing_payment_term:
                if record.amount_total == record.versement_commande + record.versement_pose + record.montant_financement:
                    record.financement_ok = True
                else:
                    record.financement_ok = False
                    # raise ValidationError("Les montants des versements et fufinacement ne correspondent pas au montant total de la commande, vérifiez les valeurs !")
    

    # === WIZARD ===#
    maison_individuelle = fields.Boolean(store=True)
    immeuble_collectif = fields.Boolean(store=True)
    appartement_individuel = fields.Boolean(store=True)
    type_local_autre = fields.Boolean(store=True)
    autre_type_local = fields.Text(store=True)

    local_habitation = fields.Boolean(store=True)
    local_affecte_moins_de_50_habitation = fields.Boolean(store=True)
    pieces_affectees_exclusivement_a_lhabitation_dans_local = fields.Boolean(store=True)
    parties_communes_immeubles_collectifs_affectes_proportion = fields.Boolean(store=True)
    proportion = fields.Integer(store=True)
    local_transforme_habitation = fields.Text(store=True)

    proprietaire = fields.Boolean(store=True)
    locataire = fields.Boolean(store=True)
    autre_qualite_client = fields.Boolean(store=True)
    qualite_client_autre = fields.Text(store=True)

    non_affectent_elements_fondations_ouvrage_facade = fields.Boolean(store=True)
    non_affectent_plus_de_5_elements_second_oeuvre = fields.Boolean(store=True)

    planchers = fields.Boolean(store=True)
    huisseries_exterieures = fields.Boolean(store=True)
    cloisons_interieures = fields.Boolean(store=True)
    installations_sanitaires = fields.Boolean(store=True)
    installations_electriques = fields.Boolean(store=True)
    systeme_chauffage = fields.Boolean(store=True)

    non_augmentation_surface_plancher_10 = fields.Boolean(store=True)
    non_surelevation_ou_addition_construction = fields.Boolean(store=True)
    atteste_travaux_amelioration_qualite_energetique = fields.Boolean(store=True)
    atteste_travaux_amelioration_qualite_energetique_5_5 = fields.Boolean(store=True)

    taux_tva = fields.Float(store=True)

    # === ACTION METHODS ===#

    def action_open_cerfa_wizard(self):
        self.ensure_one()
        return {
            "name": _("CERFA"),
            "type": "ir.actions.act_window",
            "res_model": "sale.order.cerfa",
            "view_mode": "form",
            "target": "new",
        }

    def action_generer_cerfa(
        self,
        maison_individuelle=None,
        immeuble_collectif=None,
        appartement_individuel=None,
        autre_type_local=None,
        type_local_autre=None,
        local_habitation=None,
        local_affecte_moins_de_50_habitation=None,
        pieces_affectees_exclusivement_a_lhabitation_dans_local=None,
        parties_communes_immeubles_collectifs_affectes_proportion=None,
        proportion=None,
        local_transforme_habitation=None,
        proprietaire=None,
        locataire=None,
        autre_qualite_client=None,
        qualite_client_autre=None,
        non_affectent_elements_fondations_ouvrage_facade=None,
        non_affectent_plus_de_5_elements_second_oeuvre=None,
        planchers=None,
        huisseries_exterieures=None,
        cloisons_interieures=None,
        installations_sanitaires=None,
        installations_electriques=None,
        systeme_chauffage=None,
        non_augmentation_surface_plancher_10=None,
        non_surelevation_ou_addition_construction=None,
        atteste_travaux_amelioration_qualite_energetique=None,
        atteste_travaux_amelioration_qualite_energetique_5_5=None,
        taux_tva=None,
    ):
        self.ensure_one()
        for record in self:
            record.maison_individuelle = maison_individuelle
            record.immeuble_collectif = immeuble_collectif
            record.appartement_individuel = appartement_individuel
            record.autre_type_local = autre_type_local
            record.type_local_autre = type_local_autre
            record.local_habitation = local_habitation
            record.local_affecte_moins_de_50_habitation = local_affecte_moins_de_50_habitation
            record.pieces_affectees_exclusivement_a_lhabitation_dans_local = pieces_affectees_exclusivement_a_lhabitation_dans_local
            record.parties_communes_immeubles_collectifs_affectes_proportion = parties_communes_immeubles_collectifs_affectes_proportion
            record.proportion = proportion
            record.local_transforme_habitation = local_transforme_habitation
            record.proprietaire = proprietaire
            record.locataire = locataire
            record.autre_qualite_client = autre_qualite_client
            record.qualite_client_autre = qualite_client_autre
            record.non_affectent_elements_fondations_ouvrage_facade = non_affectent_elements_fondations_ouvrage_facade
            record.non_affectent_plus_de_5_elements_second_oeuvre = non_affectent_plus_de_5_elements_second_oeuvre
            record.planchers = planchers
            record.huisseries_exterieures = huisseries_exterieures
            record.cloisons_interieures = cloisons_interieures
            record.installations_sanitaires = installations_sanitaires
            record.installations_electriques = installations_electriques
            record.systeme_chauffage = systeme_chauffage
            record.non_augmentation_surface_plancher_10 = non_augmentation_surface_plancher_10
            record.non_surelevation_ou_addition_construction = non_surelevation_ou_addition_construction
            record.atteste_travaux_amelioration_qualite_energetique = atteste_travaux_amelioration_qualite_energetique
            record.atteste_travaux_amelioration_qualite_energetique_5_5 = atteste_travaux_amelioration_qualite_energetique_5_5
            record.taux_tva = taux_tva

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        if self.is_financing_payment_term:
            if not self.financement_ok:
                raise UserError("Attention, le montant total de la commande ne correspond pas aux montants des versements et du financement. Vérifiez les valeurs !")

        channel = self.env.ref('cr2p.channel_discount_group')
        message_body = "Un nouveau devis est en attente d'approbation: {}".format(order.name)
        # Poster un message dans le canal
        if channel:
            channel.message_post(body=message_body, subtype_xmlid='mail.mt_comment')
       
        return order

    def write(self, vals):
        order = super(SaleOrder, self).write(vals)
        if self.is_financing_payment_term:
            if not self.financement_ok:
                raise UserError("Attention, le montant total de la commande ne correspond pas aux montants des versements et du financement. Vérifiez les valeurs !")
        
        return order

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Champ pour le maximum de la remise "normale"
    discount_normal_max = fields.Float(string="Remise standard", default=10.0, config_parameter='sale.discount_normal_max')

    # Champ pour le maximum autorisé en remise
    discount_max_allowed = fields.Float(string="Remise maximum autorisée", default=25.0, config_parameter='sale.discount_max_allowed')

    # Champ pour le texte du message en cas de dépassement de la remise normale
    discount_warning_message = fields.Char(string="Message d'avertissement en cas de dépassement de la remise standard", default="VENTE DEGRADEE ! La remise totale appliquée dépasse la remise standard.", config_parameter='sale.discount_warning_message')

    discount_max_warning_message = fields.Char(string="Message d'avertissement en cas de dépassement de la remise maximum autorisée", default="La remise totale appliquée dépasse la remise maximum autorisée. Vérifiez les valeurs !", config_parameter='sale.discount_max_warning_message')

    # @api.model
    # def create(self, values):
    #     # Appel de la méthode super pour créer le devis
    #     record = super(SaleOrder, self).create(values)
    #     # Logique pour envoyer la notification au groupe des administrateurs des ventes
    #     # Recherche du groupe des administrateurs des ventes
    #     sales_managers = self.env.ref('sales_team.group_sale_manager').users
    #     message = "Un nouveau devis a été créé : {}".format(record.name)
    #     # Envoi de la notification aux membres du groupe
    #     for user in sales_managers:
    #         self.env['mail.message'].create({
    #             'body': message,
    #             'model': 'sale.order',
    #             'res_id': record.id,
    #             'message_type': 'notification',
    #             'author_id': self.env.user.partner_id.id,
    #             'recipient_ids': [(4, user.partner_id.id)]
    #         })
    #     return record

    # def _update_lines_tax(self):
    #     # Déterminez ici comment mettre à jour les tax_id des lignes de commande basées sur le taux_taxe de la commande
    #     # Exemple: Modifier chaque ligne de commande pour définir son tax_id en fonction du taux_taxe de la commande
    #     for line in self.order_line:
    #         appropriate_tax = self._get_appropriate_tax(self.taux_tva)
    #         line.tax_id = [(6, 0, [appropriate_tax.id])]

    # def _get_appropriate_tax(self, taux_tva):
    #     # Implémentez la logique pour trouver le tax_id approprié basé sur le taux_taxe
    #     # Utilisez self.env['account.tax'].search([...]) pour trouver la taxe correspondante
    #     # Par exemple, retourner la première taxe trouvée qui correspond au critère
    #     tax = self.env['account.tax'].search([('amount', '>=', taux_tva)], limit=1)
    #     return tax
