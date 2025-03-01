import logging
from typing import Dict, Any, List

from jsonpath_ng import parse as jsonpath_parse
from langchain.chains import SequentialChain
from langchain.chains.base import Chain

logger = logging.getLogger(__name__)


class MapSubchain(Chain):
    """
    Chain that runs a subchain for each element in a list input

    List input is read from inputs using jsonpath set as `map_input` and mapped as
    input_variable `map_input_to`. `map_input_to` is automatically added to input_variables
    if not already present.

    Each iteration will receive the outputs of the previous iteration under the key `outputs`

    Results are output as a list under `output_key`
    """

    chain: SequentialChain  #: :meta private:
    chains: List[Chain]
    input_variables: List[str]
    map_input: str
    map_input_to: str
    output_key: str

    def __init__(self, *args, **kwargs):
        input_variables = list(kwargs.get("input_variables", []))
        map_input_to = kwargs.get("map_input_to", "map_input")
        output_key = kwargs.get("output_key", "outputs")
        memory = kwargs.get("memory", None)
        chains = kwargs.get("chains", [])

        # add input that will be mapped on each iteration
        if map_input_to not in input_variables:
            input_variables.append(map_input_to)

        if output_key not in input_variables:
            input_variables.append(output_key)

        # create internal chain
        chain = SequentialChain(
            memory=memory, chains=chains, input_variables=input_variables
        )
        kwargs["chain"] = chain

        super().__init__(*args, **kwargs)

    @property
    def _chain_type(self) -> str:
        return "ix.MapSubchain"  # pragma: no cover

    @property
    def input_keys(self) -> List[str]:
        return self.input_variables

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    async def _acall(self, inputs: Dict[str, str]) -> Dict[str, str]:
        pass  # pragma: no cover

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        map_input = self.map_input
        map_input_to = self.map_input_to

        # map input to values list
        logger.debug(
            f"MapSubchain mapping values from map_input={map_input} to map_input_to={map_input_to}"
        )
        jsonpath_expr = jsonpath_parse(map_input)
        json_matches = jsonpath_expr.find(inputs)

        if len(json_matches) == 0:
            raise ValueError(
                f"MapSubchain could not find input at {map_input} for {map_input_to} searched: {inputs}"
            )

        values = json_matches[0].value
        if not isinstance(values, list):
            raise ValueError(
                f"MapSubchain input at {map_input} is not a list: {values}"
            )

        chain_inputs = inputs.copy()

        # run chain for each value
        outputs = []
        for value in values:
            logger.debug(f"MapSubchain processing value={value}")
            iteration_inputs = chain_inputs.copy()
            iteration_inputs[map_input_to] = value
            iteration_inputs[self.output_key] = outputs
            logger.debug(f"MapSubchain iteration_inputs={iteration_inputs}")
            iteration_outputs = self.chain.run(**iteration_inputs)
            iteration_mapped_output = iteration_outputs
            logger.debug(f"MapSubchain response outputs={iteration_mapped_output}")
            outputs.append(iteration_mapped_output)

        # return as output_key
        return {self.output_key: outputs}
