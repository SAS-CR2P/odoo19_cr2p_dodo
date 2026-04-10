# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging
from datetime import date

from odoo import models, _, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class L10nFrFecInvoicingWizard(models.TransientModel):
    """
    Extension du wizard FEC standard (l10n_fr_account) pour fonctionner
    en mode Facturation seule, sans account_accountant.

    Problème résolu :
        Dans l10n_fr_account, create_fec_report_action() est un hook vide
        (retourne None). Il est censé être surchargé par account_accountant
        pour déclencher le téléchargement. Sans account_accountant,
        le bouton "Générer" ne fait strictement rien.

    Solution :
        On surcharge create_fec_report_action() pour créer une pièce jointe
        temporaire et renvoyer une action de téléchargement direct (act_url).

    Note sur la date de verrouillage (fiscalyear_lock_date) :
        La méthode generate_fec() du module parent positionne la date de
        verrouillage de l'exercice si test_file est décoché. Ce comportement
        est conservé intentionnellement : il est valide en mode Facturation
        (le champ fiscalyear_lock_date est dans le module account de base
        depuis Odoo 17). Pour éviter ce verrouillage, cocher "Mode test".
    """

    _inherit = 'l10n_fr.fec.export.wizard'

    # ------------------------------------------------------------------
    # Override principal : génération des données et blocage
    # ------------------------------------------------------------------
    
    def generate_fec(self):
        self.ensure_one()
        # Blocage de sécurité : on empêche le verrouillage du mois en cours
        # en vérifiant que la date de fin demandée n'est pas le mois actuel 
        # (sauf si l'utilisateur est judicieusement en Mode Test)
        if not self.test_file and self.date_to:
            today = fields.Date.context_today(self)
            current_month_start = today.replace(day=1)
            
            if self.date_to >= current_month_start:
                raise UserError(_(
                    "Vous générez un export FEC officiel (non-test), ce qui va verrouiller l'exercice jusqu'à la date de fin choisie (%s).\n\n"
                    "Cependant, vous ne pouvez pas verrouiller le mois en cours ni un mois futur, ce qui bloquerait par exemple le Point de Vente ou la saisie courante.\n\n"
                    "Soit vous cochez la case 'Mode test', soit vous choisissez une date de fin sur un mois totalement terminé."
                ) % self.date_to.strftime('%d/%m/%Y'))
        
        return super(L10nFrFecInvoicingWizard, self).generate_fec()

    def create_fec_report_action(self):
        """
        Surcharge du hook vide de l10n_fr_account.

        Génère le FEC via generate_fec() puis crée une pièce jointe
        temporaire pour permettre le téléchargement direct, sans
        dépendre de account_accountant.
        """
        self.ensure_one()

        # 1. Génération du contenu FEC (logique SQL dans l10n_fr_account)
        # Notre surcharge generate_fec vérifie le verrouillage juste avant
        fec_result = self.generate_fec()

        # fec_result est un dict : { 'file_name': str, 'file_content': bytes, 'file_type': str }
        file_name = fec_result.get('file_name', 'export_fec.txt')
        file_content = fec_result.get('file_content', b'')

        # 2. Création d'une pièce jointe temporaire (sera nettoyée par le GC d'Odoo)
        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'datas': base64.b64encode(file_content),
            'res_model': self._name,
            'res_id': self.id,
            'type': 'binary',
            'mimetype': 'text/plain; charset=utf-8',
        })

        _logger.info(
            'FEC généré pour %s : %s (%d octets)',
            self.env.company.name,
            file_name,
            len(file_content),
        )

        # 3. Action de téléchargement direct
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
