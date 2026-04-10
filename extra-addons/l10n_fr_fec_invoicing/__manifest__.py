# -*- coding: utf-8 -*-
{
    'name': 'France - Export FEC (Mode Facturation)',
    'version': '19.0.1.0.0',
    'category': 'Accounting/Localizations/France',
    'summary': 'Export FEC sans dépendre de l\'application Comptabilité complète',
    'description': """
Export FEC en mode Facturation uniquement
==========================================

Ce module permet de générer le Fichier des Écritures Comptables (FEC)
obligatoire en France (art. L.47 A LPF) sans nécessiter l'installation
de l'application **Comptabilité** (account_accountant).

Il suffit d'avoir uniquement l'application **Facturation** (account).

Différences avec le module standard (account_accountant) :
-----------------------------------------------------------
- Fonctionne en mode Facturation seule
- Le bouton "Générer" télécharge directement le fichier .txt
- En mode officiel (test_file décoché) : la date de verrouillage
  de l'exercice est mise à jour (comportement standard conservé)
- En mode test (test_file coché) : aucun verrouillage
- Interface entièrement en français
- Menu accessible depuis : Facturation > Rapports légaux > Export FEC

Format du fichier généré :
--------------------------
- Encodage  : UTF-8
- Séparateur : pipe '|'
- Fin de ligne : \\r\\n
- 18 colonnes conformes à la spécification officielle DGFiP
- Nom du fichier : [SIREN]FEC[AAAAMMJJ].txt
    """,
    'author': 'Fabien BIBÉ',
    'depends': [
        'l10n_fr_account',   # Contient la logique FEC (dépend de account, pas de account_accountant)
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/l10n_fr_fec_invoicing_wizard_view.xml',
        'views/l10n_fr_fec_invoicing_menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
