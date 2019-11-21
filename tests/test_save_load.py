import os

import pytest
import copy
import numpy as np
import torch
from torchy_baselines import A2C, CEMRL, PPO, SAC, TD3
from torchy_baselines.common.noise import NormalActionNoise
from torchy_baselines.common.vec_env import DummyVecEnv
from torchy_baselines.common.identity_env import IdentityEnvBox

MODEL_LIST = [
    PPO
]


@pytest.mark.parametrize("model_class", MODEL_LIST)
def test_save_load(model_class):
    """
    Test if 'save' and 'load' saves and loads model correctly
    and if 'load_parameters' and 'get_policy_parameters' work correctly

    :param model_class: (BaseRLModel) A RL model
    """
    env = DummyVecEnv([lambda: IdentityEnvBox(10)])

    # create model
    model = model_class('MlpPolicy', env, policy_kwargs=dict(net_arch=[16]), verbose=1, create_eval_env=True)

    # test action probability for given (obs, action) pair

    # Get dictionary of current parameters
    params = copy.deepcopy(model.get_policy_parameters())

    # Modify all parameters to be random values
    random_params = dict((param_name, torch.rand_like(param)) for param_name, param in params.items())
    # Update model parameters with the new zeroed values
    model.load_parameters(random_params)

    # shared items
    new_params = model.get_policy_parameters()
    shared_items = {k: params[k] for k in params if k in new_params and torch.all(torch.eq(params[k], new_params[k]))}
    # Check that at least some actions are chosen different now
    assert not len(shared_items) == len(new_params), "Selected actions did not change " \
                                                     "after changing model parameters."

    params = new_params

    # Check
    model.learn(total_timesteps=1000, eval_freq=500)
    model.save("test_save.zip")
    model = model.load("test_save")

    #check if params are still the same after load
    new_params = model.get_policy_parameters()
    shared_items = {k: params[k] for k in params if k in new_params and torch.all(torch.eq(params[k], new_params[k]))}
    # Check that at least some actions are chosen different now
    assert len(shared_items) == len(new_params), "Parameters not the same after save and load."
    os.remove("test_save.zip")
