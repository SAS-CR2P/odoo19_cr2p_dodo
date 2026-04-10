from odoo import models, api, exceptions

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):
        # Obtenez l'ID du groupe System User (l'ID peut varier selon la configuration)
        system_user_group_id = self.env.ref('base.group_system').id

        # Parcourir chaque partenaire
        for partner in self:
            # Vérifier si des devis existent pour ce partenaire
            sale_orders = self.env['sale.order'].search([('partner_id', '=', partner.id), ('state', 'not in', ['cancel', 'draft'])])
            if sale_orders:
                # Vérifier si l'utilisateur actuel est un System User
                if system_user_group_id not in self.env.user.groups_id.ids:
                    raise exceptions.UserError("Vous n'êtes pas autorisé à modifier ce contact car un devis est déjà en place.")

        return super(ResPartner, self).write(vals)