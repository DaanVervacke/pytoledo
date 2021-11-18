import json
import os
import sys

class ToledoOutput:

    def __init__(self, output_name: str, input: json) -> None:
        
        self._OUTPUT_LOCATION = os.path.join(os.getcwd(), 'output')
        self._output_name = output_name
        self._input = input

    def __call__(self) -> str:
        
        try:

            with open(os.path.join(self._OUTPUT_LOCATION, f'{self._output_name}.json'), 'w') as f:

                json.dump(self._input, f, indent=4)
                f.close()

            return f.name

        except Exception as ex:

            sys.exit(ex)