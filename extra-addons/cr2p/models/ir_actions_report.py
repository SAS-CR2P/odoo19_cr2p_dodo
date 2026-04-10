
from odoo import models, api, exceptions, _
from odoo.exceptions import UserError

import io
import logging
_logger = logging.getLogger(__name__)

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

 
    def _get_form_fields_mapping(self, order, doc_line_id_mapping=None):
        form_fields_mapping = super()._get_form_fields_mapping(order, doc_line_id_mapping=doc_line_id_mapping)
        
        form_fields_mapping.update({
            # CERFA_TVAPDF
            'nom': order.partner_id.nom or '',
            'prenom': order.partner_id.prenom or '',
            'adresse': order.partner_id.adresse or '',
            'code_postal': order.partner_id.commune.code_postal or '',
            'commune': order.partner_id.commune.name or '',
            'commune_sign': order.partner_id.commune.name or '',
            'adresse_livraison': order.partner_shipping_id.adresse_livraison or '',
            'code_postal_livraison': order.partner_id.code_postal_livraison or '',
            'commune_livraison': order.partner_id.commune_livraison.name or '',
            'maison_individuelle': order.maison_individuelle or '',
            'imeuble_collectif': order.immeuble_collectif  or '',
            'appartement_individuel': order.appartement_individuel or '',
            'autre_type_local': order.autre_type_local or '',
            'type_local_autre': order.type_local_autre or '',
            'local_habitation': order.local_habitation or '',
            'local_affecte_moins_de_50_habitation': order.local_affecte_moins_de_50_habitation or '',
            'pieces_affectees_exclusivement_a_lhabitation_dans_local': order.pieces_affectees_exclusivement_a_lhabitation_dans_local or '',
            'parties_communes_immeubles_collectifs_affectes_proportion': order.parties_communes_immeubles_collectifs_affectes_proportion or '',
            'proportion': order.proportion or '',
            'local_transforme_habitation': order.local_transforme_habitation or '',
            'proprietaire': order.proprietaire or '',
            'locataire': order.locataire or '',
            'autre_qualite_client': order.autre_qualite_client or '',
            'qualite_client_autre': order.qualite_client_autre or '',
            'non_affectent_elements_fondations_ouvrage_facade': order.non_affectent_elements_fondations_ouvrage_facade or '',
            'non_affectent_plus_de_5_elements_second_oeuvre': order.non_affectent_plus_de_5_elements_second_oeuvre or '',
            'non_augmentation_surface_plancher_10': order.non_augmentation_surface_plancher_10 or '',
            'planchers': order.planchers or '',
            'huisseries_exterieures': order.huisseries_exterieures or '',
            'cloisons_interieures': order.cloisons_interieures or '',
            'installations_sanitaires': order.installations_sanitaires or '',
            'installations_electriques': order.installations_electriques or '',
            'systeme_chauffage': order.systeme_chauffage or '',
            'non_surelevation_ou_addition_construction': order.non_surelevation_ou_addition_construction or '',
            'atteste_travaux_amelioration_qualite_energetique': order.atteste_travaux_amelioration_qualite_energetique or '',
            'atteste_travaux_amelioration_qualite_energetique_5_5': order.atteste_travaux_amelioration_qualite_energetique_5_5 or '',

            # ANNEXE 1 : Conditions de règlement PDF

            'est_comptant': True if not order.is_financing_payment_term else False,
            'est_financement': True if order.is_financing_payment_term else False,
            # COMPTANT
            'adresse_livraison_complete': order.partner_id.inlined_complete_delivery_address or '',
            'date_souhait_client_livraison': order.date_souhait_client_livraison or '',
            'date_limite_livraison': order.date_limite_livraison or '',

            'acompte_commande_pourcentage': order.acompte_commande_pourcentage or '' if not order.is_financing_payment_term else '',
            'acompte_commande_montant': order.acompte_commande_montant or '' if not order.is_financing_payment_term else '',
            'solde_fin_chantier': order.solde_fin_chantier or '' if not order.is_financing_payment_term else '',
            'payable_en': order.payable_en or '' if not order.is_financing_payment_term else '',

            # FINANCEMENT
            'versement_commande': order.versement_commande or '' if order.is_financing_payment_term else '',
            'versement_pose': order.versement_pose or '' if order.is_financing_payment_term else '',
            'montant_financement': order.montant_financement or '' if order.is_financing_payment_term else '',
            'duree_financement': order.duree_financement or '' if order.is_financing_payment_term else '',
            'nombre_mensualites' : order.nombre_mensualites or '' if order.is_financing_payment_term else '',
            'montant_mensualites_sans_assurance': order.montant_mensualites_sans_assurance or '' if order.is_financing_payment_term else '',
            'montant_mensualites_avec_assurance': order.montant_mensualites_avec_assurance or '' if order.is_financing_payment_term else '',
            'taux_annuel_nominal': order.taux_annuel_nominal or '' if order.is_financing_payment_term else '',
            'taux_annuel_effectif_global': order.taux_annuel_effectif_global or '' if order.is_financing_payment_term else '',


            'signed_on': order.signed_on,
            'signed_by': order.signed_by,
            'esignature': 'Signé électroniquement par ' + order.signed_by + ' le ' + order.signed_on.strftime('%d/%m/%Y') if order.signed_on else '',
            'user_id__phone': order.user_id.phone or '',
            'user_id_2__name': order.second_salesperson_id.name or '',
            'user_id_2__phone': order.second_salesperson_id.phone or '',
            'user_id__sign_signature': order.second_salesperson_id.sign_signature or '',
            'user_id_2__sign_signature': order.second_salesperson_id.sign_signature or '',
            #  !!! CHAMP ORIGINAUX !!!

            # 'name': order.name,
            # 'partner_id__name': order.partner_id.name,
            # 'user_id__name': order.user_id.name,
            # 'amount_untaxed': format_amount(env, order.amount_untaxed, order.currency_id),
            # 'amount_total': format_amount(env, order.amount_total, order.currency_id),
            # 'delivery_date': format_datetime(env, order.commitment_date, tz=tz),
            # 'validity_date': format_date(env, order.validity_date, lang_code=lang_code),
            # 'client_order_ref': order.client_order_ref or '',
        })
        return form_fields_mapping
