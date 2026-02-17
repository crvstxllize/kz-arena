from inspect import signature

from django.db.models.constraints import CheckConstraint


def _patch_checkconstraint_condition():
    params = signature(CheckConstraint.__init__).parameters
    if "condition" in params:
        return

    original_init = CheckConstraint.__init__

    def _compat_init(self, *args, **kwargs):
        if "condition" in kwargs and "check" not in kwargs:
            kwargs["check"] = kwargs.pop("condition")
        return original_init(self, *args, **kwargs)

    CheckConstraint.__init__ = _compat_init


_patch_checkconstraint_condition()
