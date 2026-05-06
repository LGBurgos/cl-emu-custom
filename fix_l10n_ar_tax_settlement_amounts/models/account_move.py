import inspect

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _l10n_ar_get_amounts(self, *args, **kwargs):
        """Compat layer for callers that pass base_lines as keyword argument."""
        method = super()._l10n_ar_get_amounts
        params = inspect.signature(method).parameters

        if "base_lines" in kwargs and "base_lines" not in params:
            base_lines = kwargs.pop("base_lines")
            positional_capacity = sum(
                1
                for param in params.values()
                if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            )
            # Some versions accept base lines as first positional argument.
            if base_lines is not None and not args and positional_capacity >= 1:
                args = (base_lines,)

        return method(*args, **kwargs)
