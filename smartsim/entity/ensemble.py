from os import getcwd
from smartsim.error.errors import SmartSimError
from ..error import EntityExistsError, SSUnsupportedError, UserStrategyError
from .entityList import EntityList
from .model import Model
from .strategies import create_all_permutations, random_permutations, step_values
from ..utils.helpers import init_default
from ..settings.settings import BatchSettings, RunSettings
from copy import deepcopy
from ..utils import get_logger
logger = get_logger(__name__)


class Ensemble(EntityList):
    """Ensembles are groups of Models that can be used
    for quickly generating a number of models with different
    model parameter spaces.

    Models within the default Ensemble will use their own
    run_settings, whereas models not in the default ensemble
    will inherit the run_settings of that ensemble.
    """

    def __init__(
        self, name, params, batch_settings=None, run_settings=None, perm_strat="all_perm", **kwargs
    ):
        """Initialize an Ensemble of Model instances.

        The kwargs argument can be used to pass custom input
        parameters to the permutation strategy.

        :param name: Name of the ensemble
        :type name: str
        :param params: model parameters for Model generation
        :type params: dict
        :param run_settings: settings for the launcher, defaults to {}
        :type run_settings: dict, optional
        :param perm_strat: permutation strategy for model creation,
                           options are "all_perm", "stepped", "random"
                           or a callable function
        :type perm_strat: str
        """
        self.params = init_default({}, params, dict)
        self._key_prefixing_enabled = True
        self.batch_settings = init_default({}, batch_settings, BatchSettings)
        self.run_settings = init_default({}, run_settings, RunSettings)
        super().__init__(name, getcwd(), perm_strat=perm_strat, **kwargs)

    @property
    def models(self):
        return self.entities


    def _initialize_entities(self, **kwargs):
        """Initialize all the models within the ensemble based
        on the parameters passed to the ensemble and the permuation
        strategy given at init.

        :raises UserStrategyError: if user generation strategy fails
        """
        strategy = self._set_strategy(kwargs.pop("perm_strat"))
        replicas = kwargs.pop("replicas", None)
        # if a ensemble has parameters and run settings, create
        # the ensemble and copy run_settings to each member
        if self.params:
            if self.run_settings:
                names, params = self._read_model_parameters()
                all_model_params = strategy(names, params, **kwargs)
                if not isinstance(all_model_params, list):
                    raise UserStrategyError(strategy)

                for i, param_set in enumerate(all_model_params):
                    if not isinstance(param_set, dict):
                        raise UserStrategyError(strategy)

                    model_name = "_".join((self.name, str(i)))
                    model = Model(
                        model_name,
                        param_set,
                        self.path,
                        run_settings=deepcopy(self.run_settings),
                    )
                    model.enable_key_prefixing()
                    self.add_model(model)
            # cannot generate models without run settings
            else:
                raise SmartSimError(
                    "Ensembles supplied with 'params' argument must be provided run settings")
        else:
            if self.run_settings:
                if replicas:
                    for i in range(replicas):
                        model_name = "_".join((self.name, str(i)))
                        model = Model(
                            model_name,
                            {},
                            self.path,
                            run_settings=deepcopy(self.run_settings),
                        )
                        model.enable_key_prefixing()
                        logger.debug(f"Created ensemble member: {model_name} in {self.name}")
                        self.add_model(model)
                else:
                    raise SmartSimError(
                        "Ensembles without 'params' to expand into members cannot be given run settings")
            # if no params, no run settings and no batch settings, error because we
            # don't know how to run the ensemble
            elif not self.batch_settings:
                raise SmartSimError(
                    "Ensemble must be provided batch settings or run settings")
            else:
                logger.info("Empty ensemble created for batch launch")

    def add_model(self, model):
        """Add a model to this ensemble

        :param model: model instance
        :type model: Model
        :raises EntityExistsError: if model already exists in this ensemble
        """
        if not isinstance(model, Model):
            raise TypeError(
                f"Argument to add_model was of type {type(model)}, not Model"
            )
        # "in" operator uses model name for __eq__
        if model in self.entities:
            raise EntityExistsError(
                f"Model {model.name} already exists in ensemble {self.name}"
            )
        self.entities.append(model)

    def register_incoming_entity(self, incoming_entity):
        """Register future communication between entities.

        Registers the named data sources that this entity
        has access to by storing the key_prefix associated
        with that entity

        Only python clients can have multiple incoming connections

        :param incoming_entity: The entity that data will be received from
        :type incoming_entity: SmartSimEntity
        """
        for model in self.entities:
            model.register_incoming_entity(incoming_entity)

    def enable_key_prefixing(self):
        """If called, all models within this ensemble will prefix their keys with its
        own model name.
        """
        for model in self.entities:
            model.enable_key_prefixing()

    def query_key_prefixing(self):
        """Inquire as to whether each model within the ensemble will prefix its keys

        :returns: True if all models have key prefixing enabled, False otherwise
        :rtype: dict
        """
        return all([model.query_key_prefixing() for model in self.entities])

    def attach_generator_files(self, to_copy=None, to_symlink=None, to_configure=None):
        for model in self.entities:
            model.attach_generator_files(
                to_copy=to_copy, to_symlink=to_symlink, to_configure=to_configure
            )

    def _set_strategy(self, strategy):
        """Set the permutation strategy for generating models within
        the ensemble

        :param strategy: name of the strategy or callable function
        :type strategy: str
        :raises SSUnsupportedError: if str name is not supported
        :return: strategy function
        :rtype: callable
        """
        if strategy == "all_perm":
            return create_all_permutations
        if strategy == "step":
            return step_values
        if strategy == "random":
            return random_permutations
        if callable(strategy):
            return strategy
        raise SSUnsupportedError(
            f"Permutation strategy given is not supported: {strategy}"
        )

    def _read_model_parameters(self):
        """Take in the parameters given to the ensemble and prepare to
        create models for the ensemble

        :raises TypeError: if params are of the wrong type
        :return: param names and values for permutation strategy
        :rtype: tuple
        """
        if not isinstance(self.params, dict):
            raise TypeError(
                "Ensemble initialization argument 'params' must be of type dict"
            )
        param_names = []
        parameters = []
        for name, val in self.params.items():
            param_names.append(name)
            
            if isinstance(val, list):
                parameters.append(val)
            elif isinstance(val, (int, str)):
                parameters.append([val])
            else:
                raise TypeError(
                    "Incorrect type for ensemble parameters\n"
                    + "Must be list, int, or string."
                )
        return param_names, parameters

    def __getitem__(self, index):
        return self.entities[index]
