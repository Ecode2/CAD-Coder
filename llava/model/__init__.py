try:
    from .language_model.llava_llama import LlavaLlamaForCausalLM, LlavaConfig
    from .language_model.llava_mpt import LlavaMptForCausalLM, LlavaMptConfig
    from .language_model.llava_mistral import LlavaMistralForCausalLM, LlavaMistralConfig
except:
    pass

"""
llava.model package initializer.

Expose concrete language-model classes from language_model subpackage so that
calling `from llava.model import *` provides the expected names.
"""

""" __all__ = []

_import_errors = {}

def _try_import(name, module_path, attr_names):
    try:
        mod = __import__(module_path, fromlist=attr_names)
        for a in attr_names:
            globals()[a] = getattr(mod, a)
            if a not in __all__:
                __all__.append(a)
        return True
    except Exception as e:
        _import_errors[name] = str(e)
        return False

# Try to import known language-model backends
_try_import("llama", "llava.model.language_model.llava_llama", [
    "LlavaLlamaForCausalLM", "LlavaConfig"
])
_try_import("mpt", "llava.model.language_model.llava_mpt", [
    "LlavaMptForCausalLM", "LlavaMptConfig"
])
_try_import("mistral", "llava.model.language_model.llava_mistral", [
    "LlavaMistralForCausalLM", "LlavaMistralConfig"
])

# Optionally expose any other helpers you need here.
# Keep import errors recorded for debugging (do not raise).
def import_errors():
    return dict(_import_errors)
"""