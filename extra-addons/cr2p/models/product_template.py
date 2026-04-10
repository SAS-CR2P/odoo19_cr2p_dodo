from odoo import models, fields, api, exceptions

class ProductTemplate(models.Model):
    _inherit = "product.template"

    description_sale = fields.Html(
    'Sales Description', translate=True, sanitize=False,
    help="A description of the Product that you want to communicate to your customers. "
            "This description will be copied to every Sales Order, Delivery Order and Customer Invoice/Credit Note")