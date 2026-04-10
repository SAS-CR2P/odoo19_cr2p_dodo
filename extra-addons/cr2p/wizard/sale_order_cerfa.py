# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import fields, models, api, _
from odoo import exceptions


class SaleOrderCerfa(models.TransientModel):
    _name = "sale.order.cerfa"
    _description = "CERFA Wizard"

    sale_order_id = fields.Many2one(
        "sale.order",
        default=lambda self: self.env.context.get("active_id"),
        required=True
    )

    taux_tva = fields.Float("Calcul de la TVA", compute="_compute_taux_tva", store=True)

    # # Les champs suivants sont des champs calculés qui sont liés au champ sale_order_id
    # # IDENTITE DU CLIENT OU DE SON REPRESENTANT
    # nom = fields.Char(compute='_compute_prenom_nom', store=True)
    # prenom = fields.Char(compute='_compute_prenom_nom', store=True)
    # adresse = fields.Char(related='sale_order_id.partner_id.adresse')
    # code_postal = fields.Char(related='sale_order_id.partner_id.code_postal')
    # commune = fields.Many2one(related='sale_order_id.partner_id.commune')
    # adresse_livraison = fields.Char(string='Adresse du chantier', related='sale_order_id.partner_id.adresse_livraison')
    # code_postal_livraison = fields.Char(string='Code postal', related='sale_order_id.partner_id.code_postal_livraison')
    # commune_livraison = fields.Many2one(string='Commune', related='sale_order_id.partner_id.commune_livraison')

    # NATURE DES LOCAUX
    type_local = fields.Selection(
        selection=[
            ("maison_individuelle", "Maison ou immeuble individuel"),
            ("immeuble_collectif", "Immeuble collectif"),
            ("appartement_individuel", "Appartement individuel"),
            ("autre", "Autre"),
        ],
        required=True,
        store=True,
    )
    maison_individuelle = fields.Boolean(compute="_compute_type_local", store=True)
    immeuble_collectif = fields.Boolean(compute="_compute_type_local", store=True)
    appartement_individuel = fields.Boolean(compute="_compute_type_local", store=True)
    autre_type_local = fields.Boolean(compute="_compute_type_local", store=True)
    type_local_autre = fields.Char(
        "Précisez la nature du local à usage d'habitation", store=True
    )

    @api.depends("type_local")
    def _compute_type_local(self):
        for wizard in self:
            wizard.maison_individuelle = (
                True if wizard.type_local == "maison_individuelle" else False
            )
            wizard.immeuble_collectif = (
                True if wizard.type_local == "immeuble_collectif" else False
            )
            wizard.appartement_individuel = (
                True if wizard.type_local == "appartement_individuel" else False
            )
            wizard.autre_type_local = True if wizard.type_local == "autre" else False

            if wizard.type_local != "autre":
                wizard.type_local_autre = ""

    travaux_realises_dans = fields.Selection(
        selection=[
            ("local_habitation", "Local à usage d'habitation"),
            (
                "local_affecte_moins_de_50_habitation",
                "Local affecté pour moins de 50% à l'habitation",
            ),
            (
                "parties_communes_immeubles_collectifs_affectes_proportion",
                "Partis communes d'immmeubles collectifs affectés dans une proportion de xx ‰ à l'habitation",
            ),
            (
                "local_transforme_habitation",
                "Local transformé en habitation à l'issue des travaux",
            ),
        ],
        string="Les travaux sont réalisés dans",
        required=True,
        store=True,
    )
    local_habitation = fields.Boolean(
        compute="_compute_travaux_realises_dans", store=True
    )
    local_affecte_moins_de_50_habitation = fields.Boolean(
        compute="_compute_travaux_realises_dans", store=True
    )
    parties_communes_immeubles_collectifs_affectes_proportion = fields.Integer(
        compute="_compute_travaux_realises_dans", store=True
    )
    proportion = fields.Integer("Proportion (‰)", help="Précisez la proportion en ‰")
    local_transforme_habitation = fields.Boolean(
        compute="_compute_travaux_realises_dans", store=True
    )

    @api.depends("travaux_realises_dans")
    def _compute_travaux_realises_dans(self):
        for wizard in self:
            wizard.local_habitation = (
                True if wizard.travaux_realises_dans == "local_habitation" else False
            )
            wizard.local_affecte_moins_de_50_habitation = (
                True
                if wizard.travaux_realises_dans
                == "local_affecte_moins_de_50_habitation"
                else False
            )
            wizard.parties_communes_immeubles_collectifs_affectes_proportion = (
                True
                if wizard.travaux_realises_dans
                == "parties_communes_immeubles_collectifs_affectes_proportion"
                else False
            )
            wizard.local_transforme_habitation = (
                True
                if wizard.travaux_realises_dans == "local_transforme_habitation"
                else False
            )
            if (
                wizard.travaux_realises_dans
                != "parties_communes_immeubles_collectifs_affectes_proportion"
            ):
                wizard.proportion = ""

    qualite_client = fields.Selection(
        selection=[
            ("proprietaire", "Propriétaire"),
            ("locataire", "Locataire"),
            ("autre", "Autre"),
        ],
        string="Qualité du client",
        required=True,
        store=True,
    )

    proprietaire = fields.Boolean(compute="_compute_qualite_client", store=True)
    locataire = fields.Boolean(compute="_compute_qualite_client", store=True)
    autre_qualite_client = fields.Boolean(compute="_compute_qualite_client", store=True)
    qualite_client_autre = fields.Char("Précisez la qualité du client", store=True)

    @api.depends("qualite_client")
    def _compute_qualite_client(self):
        for wizard in self:
            wizard.proprietaire = (
                True if wizard.qualite_client == "proprietaire" else False
            )
            wizard.locataire = True if wizard.qualite_client == "locataire" else False
            wizard.autre_qualite_client = (
                True if wizard.qualite_client == "autre" else False
            )
            if wizard.qualite_client != "autre":
                wizard.qualite_client_autre = ""
                

    # NATURE DES TRAVAUX
    non_affectent_elements_fondations_ouvrage_facade = fields.Boolean(store=True)
    non_affectent_plus_de_5_elements_second_oeuvre = fields.Boolean(
        compute="_compute_elements_second_oeuvre",
        store=True,
    )

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

    # CHAMPS CALCULES
    @api.depends(
        "sale_order_id.partner_id.is_company",
        "sale_order_id.partner_id.prenom",
        "sale_order_id.partner_id.prenom_correspondant",
    )
    def _compute_prenom_nom(self):
        for wizard in self:
            if wizard.sale_order_id.partner_id.is_company:
                wizard.prenom = wizard.sale_order_id.partner_id.prenom_correspondant
                wizard.nom = wizard.sale_order_id.partner_id.nom_correspondant
            else:
                wizard.prenom = wizard.sale_order_id.partner_id.prenom
                wizard.nom = wizard.sale_order_id.partner_id.nom

    @api.depends(
        "planchers",
        "huisseries_exterieures",
        "cloisons_interieures",
        "installations_sanitaires",
        "installations_electriques",
        "systeme_chauffage",
    )
    def _compute_elements_second_oeuvre(self):
        for wizard in self:
            elements = [
                wizard.planchers,
                wizard.huisseries_exterieures,
                wizard.cloisons_interieures,
                wizard.installations_sanitaires,
                wizard.installations_electriques,
                wizard.systeme_chauffage,
            ]
            wizard.non_affectent_plus_de_5_elements_second_oeuvre = (
                len([element for element in elements if element]) <= 5
            )

    @api.depends(
        "non_affectent_elements_fondations_ouvrage_facade",
        "non_affectent_plus_de_5_elements_second_oeuvre",
    )
    def _compute_taux_tva(self):
        for wizard in self:
            if (
                wizard.non_affectent_elements_fondations_ouvrage_facade
                & wizard.non_affectent_plus_de_5_elements_second_oeuvre
                & wizard.non_augmentation_surface_plancher_10
                & wizard.non_surelevation_ou_addition_construction
            ):
                wizard.taux_tva = 10
            else:
                wizard.taux_tva = 20

    def action_generer_cerfa(self):
        for wizard in self:
            if (
                wizard.non_affectent_elements_fondations_ouvrage_facade
                & wizard.non_affectent_plus_de_5_elements_second_oeuvre
                & wizard.non_augmentation_surface_plancher_10
                & wizard.non_surelevation_ou_addition_construction
            ):
            
                wizard.sale_order_id.action_generer_cerfa(
                    maison_individuelle=wizard.maison_individuelle,
                    immeuble_collectif=wizard.immeuble_collectif,
                    appartement_individuel=wizard.appartement_individuel,
                    autre_type_local=wizard.autre_type_local,
                    type_local_autre=wizard.type_local_autre,
                    local_habitation=wizard.local_habitation,
                    local_affecte_moins_de_50_habitation=wizard.local_affecte_moins_de_50_habitation,
                    parties_communes_immeubles_collectifs_affectes_proportion=wizard.parties_communes_immeubles_collectifs_affectes_proportion,
                    proportion=wizard.proportion,
                    local_transforme_habitation=wizard.local_transforme_habitation,
                    proprietaire=wizard.proprietaire,
                    locataire=wizard.locataire,
                    autre_qualite_client=wizard.autre_qualite_client,
                    qualite_client_autre=wizard.qualite_client_autre,
                    non_affectent_elements_fondations_ouvrage_facade=wizard.non_affectent_elements_fondations_ouvrage_facade,
                    non_affectent_plus_de_5_elements_second_oeuvre=wizard.non_affectent_plus_de_5_elements_second_oeuvre,
                    planchers=wizard.planchers,
                    huisseries_exterieures=wizard.huisseries_exterieures,
                    cloisons_interieures=wizard.cloisons_interieures,
                    installations_sanitaires=wizard.installations_sanitaires,
                    installations_electriques=wizard.installations_electriques,
                    systeme_chauffage=wizard.systeme_chauffage,
                    non_augmentation_surface_plancher_10=wizard.non_augmentation_surface_plancher_10,
                    non_surelevation_ou_addition_construction=wizard.non_surelevation_ou_addition_construction,
                    atteste_travaux_amelioration_qualite_energetique=wizard.atteste_travaux_amelioration_qualite_energetique,
                    atteste_travaux_amelioration_qualite_energetique_5_5=wizard.atteste_travaux_amelioration_qualite_energetique_5_5,
                    taux_tva=wizard.taux_tva,
                )
                return {'type': 'ir.actions.act_window_close'}
            else:
                raise exceptions.ValidationError(_("La TVA de 10 est applicable."))

