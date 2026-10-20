import base64
import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# 1.5 MB en bytes = 1.5 × 1024 × 1024 = 1572864
MAX_CHATTER_UPLOAD_SIZE_BYTES = 1572864


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self._is_chatter_upload(vals):
                file_size = self._get_file_size(vals)
                if file_size > MAX_CHATTER_UPLOAD_SIZE_BYTES:
                    raise UserError(
                        _(
                            "No se puede subir archivos de más de 1.5 MB.\n"
                            "Por favor, cargá el link de Drive del archivo "
                            "correspondiente en el Chatter."
                        )
                    )
        return super().create(vals_list)

    def _is_chatter_upload(self, vals):
        """
        Detecta si este adjunto viene del chatter.
        Un adjunto de chatter SIEMPRE tiene res_model + res_id
        apuntando a un modelo de negocio (no sistema/UI).
        Los adjuntos de producto/imagen también tienen res_model/res_id
        pero se diferencian porque típicamente tienen res_field seteado
        (ej: image_1920) y los del chatter no.
        """
        res_model = vals.get("res_model", "")
        if not res_model:
            return False
        # Excluir modelos de sistema
        if res_model.startswith("ir."):
            return False
        # Adjunto de chatter: tiene res_id pero NO res_field
        # (los adjuntos de producto tienden a tener res_field)
        if vals.get("res_id") and not vals.get("res_field"):
            return True
        return False

    def _get_file_size(self, vals):
        """Obtiene el tamaño real del archivo desde vals."""
        file_size = vals.get("file_size", 0)
        if file_size:
            return file_size
        datas = vals.get("datas")
        if datas:
            try:
                return len(base64.b64decode(datas))
            except Exception:
                return len(datas) * 3 // 4
        return 0