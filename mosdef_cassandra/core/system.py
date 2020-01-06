
from copy import deepcopy
import numpy as np

import mbuild
import parmed

class System(object):

    def __init__(self,boxes,species_topologies,species_in_boxes=None,
            species_to_add=None):
        """A class to contain the system to simulate in Cassandra

        A System comprises the initial simulation box(es) (empty or
        occupied), the topologies of each species to be simulated,
        and the number of each species to be added to the simulation
        box(es) prior to the start of the simulation. These three
        items are represented by ``boxes``, ``species_topologies``,
        and ``species_to_add``. If providing a box with existing
        species, you are required to specify ``species_in_boxes``,
        the number of each species that already exists.

        Each argument is specified as a list, with either one
        element for each box or one element for each species.
        Arguments must be provided as a list even in the case
        of a single species or single box.

        Parameters
        ----------
        boxes : list
            one element per box. Each element should be a
            mbuild.Compound or mbuild.Box
        species_topologies : list
            list of parmed.Structures, with one species per element
        species_in_boxes: list, optional
            one element per box. Each element is a list of length
            n_species, specifying the number of each species that
            are currently in each box
        species_to_add : list, optional
            one element per box. Each element is a list of length
            n_species, specifying the number of each species that
            should be added to each box

        Returns
        -------
        mosdef_cassandra.System
        """
        self._boxes = None
        self._species_topologies = None
        self._species_in_boxes = None
        self._species_to_add = None

        # @setter decorators used to protect boxes, species
        # topologies, and species_in_boxes from modification.
        # Error handling also occurs there
        self.boxes = boxes
        self.species_topologies = species_topologies
        self.species_in_boxes = species_in_boxes
        self.species_to_add = species_to_add

        # Error checking on number of particles in box(es)
        # vs. number from self.species_in_boxes and
        # self.species_topologies
        self.check_natoms()

    # TODO: one possibility is to return list(self._boxes)
    # rather than self._boxes --> this prevents list items from
    # being edited ¯\_(ツ)_/¯
    @property
    def boxes(self):
        return self._boxes

    @boxes.setter
    def boxes(self,boxes):
        if self._boxes is None:
            if not isinstance(boxes,list):
                raise TypeError('"boxes" should be a list. See '
                        'help(mosdef_Cassandra.System) for details.')
            for box in boxes:
                if ( not isinstance(box,mbuild.Compound) and
                     not isinstance(box,mbuild.Box) ) :
                    raise TypeError('Each box should be an '
                            'mbuild.Compound or mbuild.Box object')
            self._boxes = deepcopy(boxes)
        else:
            raise AttributeError('Box(es) cannot be modified after '
                    'System object is created. Create a new System '
                    'object if you wish to change the box(es)' )

    @property
    def species_topologies(self):
        return self._species_topologies

    @species_topologies.setter
    def species_topologies(self,species_topologies):
        if self._species_topologies is None:
            if not isinstance(species_topologies,list):
                raise TypeError('"species_topologies" should be a list. '
                        'See help(mosdef_Cassandra.System) for details.')
            for topology in species_topologies:
                if not isinstance(topology,parmed.Structure):
                    raise TypeError('Each species should be a '
                            'parmed.Structure')
            self._species_topologies = deepcopy(species_topologies)
        else:
            raise AttributeError('species_topologies cannot be '
                    'modified after System object is created. '
                    'Create a new System object if you wish to '
                    'edit the species_topolgies')

    @property
    def species_in_boxes(self):
        return list(self._species_in_boxes)

    @species_in_boxes.setter
    def species_in_boxes(self,species_in_boxes):
        if self._species_in_boxes is None:
            # Make sure species_in_boxes and species_to_add are
            # properly formatted even if use specified none
            n_species = len(self.species_topologies)
            n_boxes = len(self.boxes)
            if species_in_boxes is None:
                species_in_boxes = [[0] * n_species] * n_boxes
            # Error checking first
            if not isinstance(species_in_boxes,list):
                raise TypeError('"species_in_boxes" should be a list. '
                    'See help(mosdef_Cassandra.System) for details.')
            if len(species_in_boxes) != n_boxes:
                raise ValueError('The number of boxes inferred from the '
                    'length of "species_in_boxes" must match the '
                    'number of boxes inferred from the length of '
                    '"boxes"')
            for species_in_box in species_in_boxes:
                if not isinstance(species_in_box,list):
                    raise TypeError('"species_in_boxes" should be a list '
                            'with one list for each box.'
                            'See help(mosdef_Cassandra.System) for details.')
                if len(species_in_box) != n_species:
                    raise ValueError('The number of each species existing '
                        'in each box must be specified (even if = 0)')
                for current_n in species_in_box:
                    if not isinstance(current_n,int):
                        raise TypeError('The number of each species existing '
                                'in each box must be specified '
                                'as an integer')
            # Save data
            self._species_in_boxes = deepcopy(species_in_boxes)
        else:
            raise AttributeError('species_in_boxes cannot be '
                    'modified after System object is created. '
                    'Create a new System object if you wish to '
                    'edit species_in_boxes')

    @property
    def species_to_add(self):
        return self._species_to_add

    @species_to_add.setter
    def species_to_add(self,species_to_add):
        n_species = len(self.species_topologies)
        n_boxes = len(self.boxes)
        if species_to_add is None:
            species_to_add = [[0] * n_species] * n_boxes
        if not isinstance(species_to_add,list):
            raise TypeError('"species_to_add" should be a list. '
                'See help(mosdef_Cassandra.System) for details.')
        if len(species_to_add) != n_boxes:
            raise ValueError('The number of boxes inferred from the '
                    'length of "species_to_add" must match the '
                    'number of boxes inferred from the length of '
                    '"boxes"')
        for add_to_box in species_to_add:
            if not isinstance(add_to_box,list):
                raise TypeError('"species_to_add" should be a list '
                        'with one list for each box. '
                        'See help(mosdef_Cassandra.System) for details.')
            if len(add_to_box) != n_species:
                raise ValueError('The number of each species to '
                    'be added to each box must be specified '
                    '(even if it is = 0)')
            for add_n in add_to_box:
                if not isinstance(add_n,int):
                    raise TypeError('The number of each species to '
                            'be added to each box must be specified '
                            'as an integer')

        self._species_to_add = deepcopy(species_to_add)

    def check_natoms(self):
        """Confirm that the number of existing atoms in each box
        agrees with the number of atoms specified from the combination
        of the number of atoms in each species and the number of each
        species in the box.
        """
        n_species = len(self.species_topologies)
        n_boxes = len(self.boxes)

        atoms_per_species = [len(top.atoms) for top in self.species_topologies]
        atoms_in_box = [ np.sum(np.multiply(atoms_per_species,
                                            self.species_in_boxes[ibox]))
                         for ibox in range(n_boxes)]

        # If the box is empty it should be an mbuild.Box object. If occupied
        # it should be an mbuild.Compound object.
        for ibox,box in enumerate(self.boxes):
            if isinstance(box,mbuild.Compound):
                if box.n_particles != atoms_in_box[ibox]:
                    err_msg = ( 'The number of atoms in box {} ({}) '
                                'does not match the number of atoms '
                                'calculated to be in the box ({}) from '
                                'the number of atoms per species ({}) '
                                'and the number of species specified '
                                'in each box (species_in_boxes '
                                '= {})'.format(ibox+1,
                                               box.n_particles,
                                               atoms_in_box[ibox],
                                               atoms_per_species,
                                               self.species_in_boxes[ibox])
                              )

                    if box.n_particles == 1:
                        addtl_msg = ( 'NOTE: mbuild.Compound objects '
                                      'cannot contain zero particles. '
                                      'If you wish to specify an empty '
                                      'box please use an mbuild.Box '
                                      'object instead.')
                        raise ValueError(addtl_msg+'\n'+err_msg)
                    raise ValueError(err_msg)
            elif isinstance(box,mbuild.Box):
                if sum(self.species_in_boxes[ibox]) > 0:
                    raise ValueError('Box {} is an mbuild.Box object '
                            'but species_in_box ({}) indicates that '
                            'molecules should already be present. If you '
                            'wish to provide a starting structure for '
                            'Box {} then it must be a mbuild.Compound '
                            'object'.format(ibox+1,
                                            self.species_in_boxes[ibox],
                                            ibox+1))

