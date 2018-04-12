###################################################################
# DO NOT TOUCH THIS CODE -- BEGIN
###################################################################
import threading

def synchronized_method(method):

    outer_lock = threading.Lock()
    lock_name = "__"+method.__name__+"_lock"+"__"

    def sync_method(self, *args, **kws):
        with outer_lock:
            if not hasattr(self, lock_name): setattr(self, lock_name, threading.Lock())
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)

    return sync_method

class Singleton:

    def __init__(self, decorated):
        self._decorated = decorated

    @synchronized_method
    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

###################################################################
# DO NOT TOUCH THIS CODE -- END
###################################################################


from syned.beamline.beamline_element import BeamlineElement

from rafry.raytracer.beam import Beam

class RaytracingElements(object):
    def __init__(self):
        self.__raytracing_elements = []

    def add_beamline_element(self, beamline_element=BeamlineElement()):
        if beamline_element is None: raise ValueError("Beamline is None")

        self.__raytracing_elements.append(beamline_element)

    def add_beamline_elements(self, beamline_elements=[]):
        if beamline_elements is None: raise ValueError("Beamline is None")

        for beamline_element in beamline_elements:
            self.add_beamline_element(beamline_element)

    def get_raytracing_elements_number(self):
        return len(self.__raytracing_elements)

    def get_raytracing_elements(self):
        return self.__raytracing_elements

    def get_raytracing_element(self, index):
        return self.__raytracing_elements[index]

class RaytracingParameters(object):
    def __init__(self,
                 beam = Beam(),
                 raytracing_elements = RaytracingElements()):
        self._beam = beam
        self._raytracing_elements = raytracing_elements
        self._additional_parameters = None

    def get_beam(self):
        return self._beam

    def get_RaytracingElements(self):
        return self._raytracing_elements

    def set_additional_parameters(self, key, value):
        if self._additional_parameters is None:
            self._additional_parameters = {key : value}
        else:
            self._additional_parameters[key] = value

    def get_additional_parameter(self, key):
        return self._additional_parameters[key]

    def has_additional_parameter(self, key):
        return key in self._additional_parameters

class AbstractRaytracer(object):

    def __init__(self):
        super().__init__()

    def get_handler_name(self):
        raise NotImplementedError("This method is abstract")

    def is_handler(self, handler_name):
        return handler_name == self.get_handler_name()

    def do_raytracing(self, parameters=RaytracingParameters()):
        raise NotImplementedError("This method is abstract" +
                                  "\n\naccepts " + RaytracingParameters.__module__ + "." + RaytracingParameters.__name__ +
                                  "\nreturns " + Beam.__module__ + "." + Beam.__name__)


@Singleton
class RaytracingManager(object):

    def __init__(self):
        self.__raytracing_chain_of_responsibility = []

    @synchronized_method
    def add_raytracer(self, raytracer=AbstractRaytracer()):
        if raytracer is None: raise ValueError("Given raytracer is None")
        if not isinstance(raytracer, AbstractRaytracer): raise ValueError("Given raytracer is not a compatible object")

        for existing in self.__raytracing_chain_of_responsibility:
            if existing.is_handler(raytracer.get_handler_name()):
                raise ValueError("Raytracer already in the Chain")

        self.__raytracing_chain_of_responsibility.append(raytracer)

    def do_raytracing(self, raytracing_parameters, handler_name):
        for raytracer in self.__raytracing_chain_of_responsibility:
            if raytracer.is_handler(handler_name):
                return raytracer.do_raytracing(parameters=raytracing_parameters)

        raise Exception("Handler not found: "+handler_name)

# ---------------------------------------------------------------

class Raytracer(AbstractRaytracer):

    def __init__(self):
        super().__init__()

    def do_raytracing(self, parameters=RaytracingParameters()):
        beam = parameters.get_beam()

        for element in parameters.get_RaytracingElements().get_raytracing_elements():
            beam = element.get_optical_element().trace_optical_element(beam, element.get_coordinates())

        return beam


