# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and new-style classes.
import _pyicewmcphw
def _swig_setattr(self,class_type,name,value):
    if (name == "this"):
        if isinstance(value, class_type):
            self.__dict__[name] = value.this
            if hasattr(value,"thisown"): self.__dict__["thisown"] = value.thisown
            del value.thisown
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    self.__dict__[name] = value

def _swig_getattr(self,class_type,name):
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0


do_init = _pyicewmcphw.do_init

do_uninit = _pyicewmcphw.do_uninit

get_hw_result_count = _pyicewmcphw.get_hw_result_count

probe_hardware = _pyicewmcphw.probe_hardware

get_search_result_line = _pyicewmcphw.get_search_result_line

cvar = _pyicewmcphw.cvar

