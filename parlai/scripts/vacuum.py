#!/usr/bin/env python3

"""
Reduces the size of a model file by stripping the optimizer.

Assumes we are working with a TorchAgent
"""

import os
import torch

from parlai.core.params import ParlaiParser
from parlai.core.script import ParlaiScript, register_script
from parlai.utils.torch import atomic_save
import parlai.utils.pickle
import parlai.utils.logging as logging


@register_script("vacuum")
class Vacuum(ParlaiScript):
    @classmethod
    def setup_args(cls):
        parser = ParlaiParser(False, False)
        parser.add_argument('path', help="Path to model file.")
        return parser

    def run(self):
        self.opt.log()
        model_file = self.opt['path']
        logging.info(f"Loading {model_file}")
        states = torch.load(
            model_file,
            map_location=lambda cpu, _: cpu,
            pickle_module=parlai.utils.pickle,
        )
        logging.info(f"Backing up {model_file} to {model_file}.unvacuumed")
        os.rename(model_file, model_file + ".unvacuumed")
        for key in [
            'optimizer',
            'optimizer_type',
            'lr_scheduler',
            'lr_scheduler_type',
            'warmup_scheduler',
            'number_training_updates',
        ]:
            if key in states:
                logging.info(f"Deleting key {key}")
                del states[key]
        keys = ", ".join(states.keys())
        logging.info(f"Remaining keys: {keys}")
        logging.info(f"Saving to {model_file}")
        atomic_save(states, model_file)
