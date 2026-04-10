# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import is_html_empty


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # ---- Champs devis / produit (kanban badges) ----
    cr2p_quote_status = fields.Selection([
        ('draft', 'Brouillon'),
        ('accepted', 'Accepté'),
        ('cancelled', 'Annulé'),
        ('invoiced', 'Facturé'),
        ('refused', 'Refusé'),
    ], string='État du devis', tracking=True)

    cr2p_quote_amount = fields.Monetary(
        string='Montant devis',
        currency_field='company_currency',
    )

    cr2p_product_type_ids = fields.Many2many(
        'crm.lead.product.type',
        'crm_lead_product_type_rel',
        'lead_id', 'product_type_id',
        string='Types de produit',
    )

    # ---- Debriefing ----
    cr2p_debrief = fields.Html(
        string='Debriefing',
        tracking=True,
    )
    cr2p_debrief_done = fields.Boolean(
        string='Debriefing effectué',
        compute='_compute_cr2p_debrief_done',
        store=True,
    )

    @api.depends('cr2p_debrief')
    def _compute_cr2p_debrief_done(self):
        for lead in self:
            lead.cr2p_debrief_done = bool(lead.cr2p_debrief) and not is_html_empty(lead.cr2p_debrief)

    def write(self, vals):
        if 'stage_id' in vals:
            new_stage = self.env['crm.stage'].browse(vals['stage_id'])
            for lead in self:
                if lead.stage_id.id == vals['stage_id']:
                    continue
                self._cr2p_check_stage_transition(lead, lead.stage_id, new_stage)
                # Réinitialiser le debriefing quand on change d'étape
                # (pour obliger un nouveau debrief à chaque étape)
            if 'cr2p_debrief' not in vals:
                vals['cr2p_debrief'] = False
        return super().write(vals)

    def _cr2p_check_stage_transition(self, lead, old_stage, new_stage):
        """Vérifie les règles de transition entre étapes CR2P."""
        stage_r1 = self.env.ref('crm_cr2p.cr2p_stage_r1', raise_if_not_found=False)
        stage_r2 = self.env.ref('crm_cr2p.cr2p_stage_r2', raise_if_not_found=False)
        stage_proposition = self.env.ref('crm_cr2p.cr2p_stage_proposition', raise_if_not_found=False)
        stage_non_valide = self.env.ref('crm_cr2p.cr2p_stage_non_valide', raise_if_not_found=False)

        # Pas de vérification si les stages CR2P ne sont pas installés
        if not all([stage_r1, stage_r2, stage_proposition, stage_non_valide]):
            return

        # --- Depuis R1 : debriefing obligatoire ---
        if old_stage == stage_r1 and new_stage != old_stage:
            if not lead.cr2p_debrief_done:
                raise UserError(_(
                    "Vous devez remplir le debriefing avant de quitter l'étape R1."
                ))

        # --- Depuis R2 : debriefing obligatoire ---
        if old_stage == stage_r2 and new_stage != old_stage:
            if not lead.cr2p_debrief_done:
                raise UserError(_(
                    "Vous devez remplir le debriefing avant de quitter l'étape R2."
                ))

        # --- Depuis Proposition vers Lead non valide : debriefing obligatoire ---
        if old_stage == stage_proposition and new_stage == stage_non_valide:
            if not lead.cr2p_debrief_done:
                raise UserError(_(
                    "Vous devez remplir le debriefing avant de passer en 'Lead non valide' depuis 'Proposition'."
                ))

