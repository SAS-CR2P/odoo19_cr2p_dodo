# -*- coding: utf-8 -*-
{
    'name': 'CRM CR2P',
    'version': '19.0.1.2.0',
    'category': 'Sales/CRM',
    'summary': 'Personnalisation CRM CR2P',
    'description': """
        - Supprime commercial_partner_id, partner_id affiche les sociétés.
        - Badges kanban : état devis, montant, types de produit (PV/BP/PAC).
        - Pipeline CR2P : Nouveau → R1 → R2 → Proposition → Devis Signé / Lead non valide.
        - Debriefing obligatoire pour quitter R1, R2, ou aller en Lead non valide depuis Proposition.
    """,
    'depends': ['crm'],
    'data': [
        'security/ir.model.access.csv',
        'data/crm_lead_product_type_data.xml',
        'data/crm_stage_data.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
