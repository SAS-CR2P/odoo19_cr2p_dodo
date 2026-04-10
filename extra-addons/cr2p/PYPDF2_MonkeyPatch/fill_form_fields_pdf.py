
import logging

from PyPDF2.generic import NameObject, IndirectObject, BooleanObject, NumberObject, TextStringObject, ArrayObject, DictionaryObject, FloatObject
from odoo.tools import pdf

_logger = logging.getLogger(__name__)

orig_fill_form_fields_pdf = pdf.fill_form_fields_pdf

def fill_form_fields_pdf(writer, form_fields):
    ''' Fill in the form fields of a PDF
    :param writer: a PdfFileWriter object
    :param dict form_fields: a dictionary of form fields to update in the PDF
    :return: a filled PDF datastring
    '''

    # This solves a known problem with PyPDF2, where with some pdf software, forms fields aren't
    # correctly filled until the user click on it, see: https://github.com/py-pdf/pypdf/issues/355
    if hasattr(writer, 'set_need_appearances_writer'):
        writer.set_need_appearances_writer()

    nbr_pages = len(writer.pages)

    for page_id in range(0, nbr_pages):
        page = writer.pages[page_id]

        writer.update_page_form_field_values(page, form_fields)

        for raw_annot in page.get('/Annots', []):
            annot = raw_annot.getObject()
            _logger.info(annot)
            for field in form_fields:
                # _logger.info(annot)
                if annot.get('/T') == field and annot.get('/V') == 'True':
                    ap_n = annot.get("/AP", {}).get("/N")
                    if ap_n:
                        keys_list = list(ap_n.keys())
                        if keys_list:
                            key = keys_list[0]
                            annot.update({
                                NameObject("/V"): NameObject(key),
                                NameObject("/AS"): NameObject(key),
                            })
                    else:
                        _logger.warning("Annotation AP/N does not exist or is empty for field: %s", field)
                # Mark filled fields as readonly to avoid the blue overlay:
                if annot.get('/T') == field:
                    annot.update({NameObject("/Ff"): NumberObject(1)})
                
    return orig_fill_form_fields_pdf(writer, form_fields)

pdf.fill_form_fields_pdf = fill_form_fields_pdf