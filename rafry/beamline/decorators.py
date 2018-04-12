
from rafry.raytracer.beam import Beam

class LightSourceDecorator():

    def generate_source(self, source_parameters):
        raise NotImplementedError("This method should be specialized by specific implementors" +
                                  "\n\nreturns " + Beam.__module__ + "." + Beam.__name__)


class OpticalElementDecorator(object):

    def __init__(self):
        super().__init__()

    def trace_optical_element(self, beam=Beam(), parameters=None):
        raise NotImplementedError("This method should be specialized by specific implementors" +
                                  "\n\naccepts " + Beam.__module__ + "." + Beam.__name__ +
                                  "\nreturns " + Beam.__module__ + "." + Beam.__name__)
