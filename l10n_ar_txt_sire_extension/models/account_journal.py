import re

from odoo import _, fields, models
from odoo.addons.l10n_ar_account_tax_settlement.models.account_journal import remove_accents_and_dieresis
from odoo.exceptions import RedirectWarning


class AccountJournal(models.Model):
    _inherit = "account.journal"

    settlement_tax = fields.Selection(
        selection_add=[
            ("sire_f2004", "TXT SIRE Seguridad Social (F2004)"),
            ("sire_f2005", "TXT SIRE Retención Impositiva (F2005)"),
        ]
    )

    # ─────────────────────────────────────────────────────────────────────────
    # F2004 — CERTIFICADOS SEGURIDAD SOCIAL  (Impuesto 353)
    # Especificación: apartado 4 del PDF SIRE-especificacion-para-emision-por-lote
    # Longitud de línea: 191 caracteres + CRLF
    # ─────────────────────────────────────────────────────────────────────────

    def sire_f2004_files_values(self, move_lines):
        """Genera Retenciones_sire_f2004.txt para Seguridad Social (F2004).

        Diseño de registro (191 chars + CRLF):
        #  Campo                         Tipo     Long  Desde  Hasta
        1  FORMULARIO                    Integer     4      1      4   -> fijo "2004"
        2  VERSION                       Integer     4      5      8   -> fijo "0100"
        3  CODIGO DE TRAZABILIDAD        String     10      9     18   -> espacios
        4  CUIT AGENTE                   Integer    11     19     29   -> company.vat
        5  IMPUESTO                      Integer     3     30     32   -> fijo "353"
        6  REGIMEN                       Integer     3     33     35   -> tax.l10n_ar_code
        7  CUIT RETENIDO                 Integer    11     36     46   -> partner.l10n_ar_vat
        8  FECHA RETENCION               Date       10     47     56   -> dd/mm/yyyy
        9  TIPO COMPROBANTE              Integer     2     57     58   -> "06"
        10 FECHA COMPROBANTE             Date       10     59     68   -> dd/mm/yyyy
        11 NRO COMPROBANTE               String     16     69     84   -> payment.name (solo digitos)
        12 IMPORTE COMPROBANTE           Decimal    14     85     98   -> payment.payment_total
        13 IMPORTE RETENCION             Decimal    14     99    112   -> abs(line.balance)
        14 CERTIFICADO ORIGINAL NRO      Integer    25    113    137   -> espacios
        15 CERTIFICADO ORIGINAL FECHA    Date       10    138    147   -> espacios
        16 CERTIFICADO ORIGINAL IMPORTE  Decimal    14    148    161   -> espacios
        17 OTROS DATOS                   String     30    162    191   -> espacios
        """
        self.ensure_one()
        content = ""
        self._sire_f2004_validations(move_lines)
        for line in move_lines.sorted(key=lambda r: (r.date, r.id)):
            payment = line.payment_id
            company_vat = payment.company_id.vat
            fecha_impuesto = line.date.strftime("%d/%m/%Y")
            tax = line._get_settlement_tax()

            # 1  FORMULARIO (integer 4, 1-4) -> fijo "2004"
            content += "2004"
            # 2  VERSION (integer 4, 5-8) -> fijo "0100"
            content += "0100"
            # 3  CODIGO DE TRAZABILIDAD (string 10, 9-18) -> espacios
            content += " " * 10
            # 4  CUIT AGENTE (integer 11, 19-29)
            content += company_vat
            # 5  IMPUESTO (integer 3, 30-32) -> fijo "353"
            content += "353"
            # 6  REGIMEN (integer 3, 33-35)
            content += tax.l10n_ar_code.zfill(3)
            # 7  CUIT RETENIDO (integer 11, 36-46) -> CUIT argentino del partner
            content += line.partner_id.l10n_ar_vat
            # 8  FECHA RETENCION (date 10, 47-56)
            content += fecha_impuesto
            # 9  TIPO COMPROBANTE (integer 2, 57-58) -> "06" retencion
            content += "06"
            # 10 FECHA COMPROBANTE (date 10, 59-68)
            content += fecha_impuesto
            # 11 NRO COMPROBANTE (string 16, 69-84) -> solo digitos, justificado a la izquierda
            content += re.sub("[^0-9]", "", payment.name).ljust(16)
            # 12 IMPORTE COMPROBANTE (decimal 14, 85-98)
            content += "%014.2f" % abs(payment.payment_total)
            # 13 IMPORTE RETENCION (decimal 14, 99-112)
            content += "%014.2f" % abs(line.balance)
            # 14 CERTIFICADO ORIGINAL NRO (integer 25, 113-137) -> espacios
            content += " " * 25
            # 15 CERTIFICADO ORIGINAL FECHA RETEN (date 10, 138-147) -> espacios
            content += " " * 10
            # 16 CERTIFICADO ORIGINAL IMPORTE (decimal 14, 148-161) -> espacios
            content += " " * 14
            # 17 OTROS DATOS (string 30, 162-191) -> espacios
            content += " " * 30
            content += "\r\n"
        return [{"txt_filename": "Retenciones_sire_f2004.txt", "txt_content": remove_accents_and_dieresis(content)}]

    def _sire_f2004_validations(self, move_lines):
        """Validaciones previas a la generacion del F2004."""
        for line in move_lines.sorted(key=lambda r: (r.date, r.id)):
            tax = line._get_settlement_tax()
            if not tax.l10n_ar_code:
                raise RedirectWarning(
                    message=_(
                        "El impuesto '%(tax_name)s' (id: %(tax_id)s) no tiene codigo de regimen"
                        " establecido. Es obligatorio para generar el archivo TXT SIRE F2004."
                        " Editar campo 'Codigo AFIP' (l10n_ar_code) en la vista formulario del impuesto.",
                        tax_id=tax.id,
                        tax_name=tax.name,
                    ),
                    action=tax.get_formview_action(),
                    button_text=_("Editar impuesto"),
                )
            if not line.partner_id.l10n_ar_vat:
                raise RedirectWarning(
                    message=_(
                        "El contacto '%(name)s' (id: %(id)s) no tiene CUIT/CUIL establecido."
                        " Es obligatorio para generar el archivo TXT SIRE F2004.",
                        name=line.partner_id.name,
                        id=line.partner_id.id,
                    ),
                    action=line.partner_id.get_formview_action(),
                    button_text=_("Editar contacto"),
                )

    # ─────────────────────────────────────────────────────────────────────────
    # F2005 — CERTIFICADOS DE RETENCION IMPOSITIVA  (Impuesto 216)
    # Especificacion: apartado 5 del PDF SIRE-especificacion-para-emision-por-lote
    # Longitud de linea: 305 caracteres + CRLF
    # ─────────────────────────────────────────────────────────────────────────

    def sire_f2005_files_values(self, move_lines):
        """Genera Retenciones_sire_f2005.txt para Retencion Impositiva (F2005).

        Diseno de registro (305 chars + CRLF):
        #  Campo                                   Tipo     Long  Desde  Hasta
        1  VERSION                                 Integer     4      1      4   -> fijo "0100"
        2  CODIGO DE TRAZABILIDAD                  String     36      5     40   -> espacios
        3  IMPUESTO                                Integer     3     41     43   -> fijo "216"
        4  REGIMEN                                 Integer     3     44     46   -> tax.l10n_ar_code
        5  FECHA RETENCION                         Date       10     47     56   -> dd/mm/yyyy
        6  CONDICION                               Integer     2     57     58   -> espacios
        7  IMPOSIBILIDAD DE RETENCION              Boolean     1     59     59   -> "0"
        8  NO RETENCION MOTIVO                     String     30     60     89   -> espacios
        9  IMPORTE RETENCION                       Decimal    14     90    103   -> abs(line.balance)
        10 IMPORTE DE LA BASE DE CALCULO/CANTIDAD  Decimal    14    104    117   -> abs(withholding.base_amount)
        11 REGIMEN DE EXCLUSION                    Boolean     1    118    118   -> "0"
        12 PORCENTAJE DE EXCLUSION                 Decimal     6    119    124   -> "      " o tax.porcentaje_exclusion
        13 FECHA PUBLICACION VIGENCIA              Date       10    125    134   -> espacios
        14 TIPO COMPROBANTE                        Integer     2    135    136   -> "06"
        15 FECHA COMPROBANTE                       Date       10    137    146   -> dd/mm/yyyy
        16 NRO COMPROBANTE                         String     16    147    162   -> payment.name (solo digitos)
        17 COE                                     String     12    163    174   -> espacios
        18 COE ORIGINAL                            String     12    175    186   -> espacios
        19 CAE                                     String     14    187    200   -> espacios
        20 IMPORTE COMPROBANTE                     Decimal    14    201    214   -> payment.payment_total
        21 MOTIVO EMISION NOTA CREDITO/AJUSTE      String     30    215    244   -> espacios
        22 RETENIDO CLAVE                          Integer    11    245    255   -> l10n_ar_vat o CUIT del pais
        23 CERTIFICADO ORIGINAL NRO                String     25    256    280   -> espacios
        24 CERTIFICADO ORIGINAL FECHA RETEN        Date       10    281    290   -> espacios
        25 CERTIFICADO ORIGINAL IMPORTE            Decimal    14    291    304   -> espacios
        26 MOTIVO DE LA ANULACION                  Integer     1    305    305   -> espacio
        """
        self.ensure_one()
        content = ""
        self._sire_f2005_validations(move_lines)
        for line in move_lines.sorted(key=lambda r: (r.date, r.id)):
            payment = line.payment_id
            tax = line._get_settlement_tax()
            fecha_impuesto = line.date.strftime("%d/%m/%Y")

            # 1  VERSION (integer 4, 1-4) -> fijo "0100"
            content += "0100"
            # 2  CODIGO DE TRAZABILIDAD (string 36, 5-40) -> espacios
            content += " " * 36
            # 3  IMPUESTO (integer 3, 41-43) -> fijo "216"
            content += "216"
            # 4  REGIMEN (integer 3, 44-46)
            content += tax.l10n_ar_code.zfill(3)
            # 5  FECHA RETENCION (date 10, 47-56)
            content += fecha_impuesto
            # 6  CONDICION (integer 2, 57-58) -> espacios (se completa segun tabla CONDICION)
            content += " " * 2
            # 7  IMPOSIBILIDAD DE RETENCION (boolean 1, 59-59) -> "0" retencion efectuada
            content += "0"
            # 8  NO RETENCION MOTIVO (string 30, 60-89) -> espacios (obligatorio si campo 7=1)
            content += " " * 30
            # 9  IMPORTE RETENCION (decimal 14, 90-103)
            content += "%014.2f" % abs(line.balance)
            # 10 IMPORTE BASE CALCULO/CANTIDAD (decimal 14, 104-117)
            content += "%014.2f" % abs(line.withholding_id.base_amount)
            # 11 REGIMEN DE EXCLUSION (boolean 1, 118-118) -> "0" no excluido
            content += "0"
            # 12 PORCENTAJE DE EXCLUSION (decimal 6, 119-124) -> solo obligatorio si campo 11=1
            porcentaje = getattr(tax, "porcentaje_exclusion", 0.0) or 0.0
            content += "%06.2f" % porcentaje if porcentaje else " " * 6
            # 13 FECHA PUBLICACION O FINALIZACION DE LA VIGENCIA (date 10, 125-134) -> espacios
            content += " " * 10
            # 14 TIPO COMPROBANTE (integer 2, 135-136) -> "06" retencion
            content += "06"
            # 15 FECHA COMPROBANTE (date 10, 137-146)
            content += fecha_impuesto
            # 16 NRO COMPROBANTE (string 16, 147-162) -> solo digitos, justificado a la izquierda
            content += re.sub("[^0-9]", "", payment.name).ljust(16)
            # 17 COE (string 12, 163-174) -> espacios
            content += " " * 12
            # 18 COE ORIGINAL (string 12, 175-186) -> espacios
            content += " " * 12
            # 19 CAE (string 14, 187-200) -> espacios
            content += " " * 14
            # 20 IMPORTE COMPROBANTE (decimal 14, 201-214)
            content += "%014.2f" % abs(payment.payment_total)
            # 21 MOTIVO EMISION NOTA DE CREDITO/AJUSTE (string 30, 215-244) -> espacios
            content += " " * 30
            # 22 RETENIDO CLAVE (integer 11, 245-255) -> CUIT/CUIL/CDI del retenido
            is_exterior = (
                line.partner_id.l10n_ar_afip_responsibility_type_id.id
                == self.env.ref("l10n_ar.res_EXT").id
            )
            if is_exterior:
                pais = line.partner_id.country_id
                content += pais.l10n_ar_legal_entity_vat or pais.l10n_ar_natural_vat or " " * 11
            else:
                content += line.partner_id.l10n_ar_vat or " " * 11
            # 23 CERTIFICADO ORIGINAL NRO (string 25, 256-280) -> espacios
            content += " " * 25
            # 24 CERTIFICADO ORIGINAL FECHA RETEN (date 10, 281-290) -> espacios
            content += " " * 10
            # 25 CERTIFICADO ORIGINAL IMPORTE (decimal 14, 291-304) -> espacios
            content += " " * 14
            # 26 MOTIVO DE LA ANULACION (integer 1, 305-305) -> espacio
            content += " "
            content += "\r\n"
        return [{"txt_filename": "Retenciones_sire_f2005.txt", "txt_content": remove_accents_and_dieresis(content)}]

    def _sire_f2005_validations(self, move_lines):
        """Validaciones previas a la generacion del F2005."""
        for line in move_lines.sorted(key=lambda r: (r.date, r.id)):
            tax = line._get_settlement_tax()
            if not tax.l10n_ar_code:
                raise RedirectWarning(
                    message=_(
                        "El impuesto '%(tax_name)s' (id: %(tax_id)s) no tiene codigo de regimen"
                        " establecido. Es obligatorio para generar el archivo TXT SIRE F2005."
                        " Editar campo 'Codigo AFIP' (l10n_ar_code) en la vista formulario del impuesto.",
                        tax_id=tax.id,
                        tax_name=tax.name,
                    ),
                    action=tax.get_formview_action(),
                    button_text=_("Editar impuesto"),
                )
            is_exterior = (
                line.partner_id.l10n_ar_afip_responsibility_type_id.id
                == self.env.ref("l10n_ar.res_EXT").id
            )
            if not is_exterior and not line.partner_id.l10n_ar_vat:
                raise RedirectWarning(
                    message=_(
                        "El contacto '%(name)s' (id: %(id)s) no tiene CUIT/CUIL/CDI establecido."
                        " Es obligatorio para generar el archivo TXT SIRE F2005.",
                        name=line.partner_id.name,
                        id=line.partner_id.id,
                    ),
                    action=line.partner_id.get_formview_action(),
                    button_text=_("Editar contacto"),
                )
            if is_exterior:
                pais = line.partner_id.country_id
                if not pais:
                    raise RedirectWarning(
                        message=_(
                            "El contacto '%s' debe tener pais establecido.",
                            line.partner_id.name,
                        ),
                        action=line.partner_id.get_formview_action(),
                        button_text=_("Editar contacto"),
                    )
                if not pais.l10n_ar_legal_entity_vat and not pais.l10n_ar_natural_vat:
                    raise RedirectWarning(
                        message=_(
                            "El pais '%(pais)s' no tiene CUIT para personas juridicas ni fisicas establecido.",
                            pais=pais.name,
                        ),
                        action=pais.get_formview_action(),
                        button_text=_("Editar Pais"),
                    )
