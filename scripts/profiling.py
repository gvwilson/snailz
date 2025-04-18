from pathlib import Path
import random

from snailz.scenario import ScenarioParams, ScenarioData

OUTPUT = Path("data")

parameters = ScenarioParams()
random.seed(parameters.seed)
data = ScenarioData.generate(parameters)
ScenarioData.save(OUTPUT, data, full=True)
