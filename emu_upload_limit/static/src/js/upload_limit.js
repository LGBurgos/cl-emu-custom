/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { AttachmentUploadService } from "@mail/core/common/attachment_upload_service";

const MAX_CHATTER_UPLOAD_SIZE = 1572864; // 1.5 MB en bytes
const CUSTOM_MESSAGE =
    "No se puede subir archivos de más de 1.5 MB.\n" +
    "Por favor, cargá el link de Drive del archivo correspondiente en el Chatter.";

patch(AttachmentUploadService.prototype, {
    async upload(thread, composer, file, options) {
        if (file && file.size > MAX_CHATTER_UPLOAD_SIZE) {
            this.notificationService.add(CUSTOM_MESSAGE, {
                type: "danger",
                sticky: true,
            });
            // Return early — don't upload, don't throw (avoids UncaughtPromiseError)
            return;
        }
        return super.upload(thread, composer, file, options);
    },
});