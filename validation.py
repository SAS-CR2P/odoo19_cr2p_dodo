from lxml import etree
import sys
try:
    rng = etree.RelaxNG(etree.parse("search_view.rng"))
    arch = """<search string="Search Partner">
                    <field name="name"
                        filter_domain="['|', '|', '|', '|', '|', '|', '|', ('name', 'ilike', self), ('prenom', '=', self), ('nom', '=', self), ('prenom2', 'ilike', self), ('nom2', 'ilike', self), ('email', 'ilike', self), ('vat', 'ilike', self), ('company_registry', 'ilike', self)]" />
                    <field name="code" string="Code" />
                    <field name="parent_id" domain="[('is_company', '=', True)]" operator="child_of" />
                    <field name="email"
                        filter_domain="['|', ('email', 'ilike', self), ('email2', 'ilike', self)]" />
                    <field name="phone"
                        filter_domain="['|', ('phone', 'ilike', self), ('phone2', 'ilike', self)]" />
                    <field name="category_id" string="Tag" operator="child_of" />
                    <field name="user_id" />
                    <separator />
                    <filter string="Particuliers" name="type_person"
                        domain="[('is_company', '=', False)]" />
                    <filter string="Fiches jointes" name="ajouter_contact2"
                        domain="[('ajouter_contact2', '=', True)]" />
                    <filter string="Sociétés" name="type_company"
                        domain="[('is_company', '=', True)]" />
                    <separator />
                    <filter string="Archived" name="inactive" domain="[('active', '=', False)]" />
                    <separator />
                    <group expand="0" name="group_by" string="Group By">
                        <filter name="salesperson" string="Salesperson" domain="[]"
                            context="{'group_by' : 'user_id'}" />
                        <filter name="group_company" string="Communes"
                            context="{'group_by': 'commune'}" />
                        <filter name="group_country" string="Départements"
                            context="{'group_by': 'departement'}" />
                    </group>
                </search>"""
    doc = etree.fromstring(arch)
    rng.assertValid(doc)
    print("VALID!")
except etree.DocumentInvalid as e:
    print(f"INVALID: {e}")
except Exception as e:
    print(f"ERROR: {e}")
