import numpy.testing as npt
import pandas as pd
import pytest

from .. import lcm


@pytest.fixture
def choosers():
    return pd.DataFrame(
        {'var1': range(5, 10),
         'thing_id': ['a', 'c', 'e', 'g', 'i']})


@pytest.fixture
def alternatives():
    return pd.DataFrame(
        {'var2': range(10, 20),
         'var3': range(20, 30)},
        index=pd.Index([x for x in 'abcdefghij'], name='thing_id'))


def test_unit_choice_uniform(choosers, alternatives):
    probabilities = [1] * len(alternatives)
    choices = lcm.unit_choice(
        choosers.index, alternatives.index, probabilities)
    npt.assert_array_equal(choices.index, choosers.index)
    assert choices.isin(alternatives.index).all()


def test_unit_choice_some_zero(choosers, alternatives):
    probabilities = [0, 1, 0, 1, 1, 0, 1, 0, 0, 1]
    choices = lcm.unit_choice(
        choosers.index, alternatives.index, probabilities)
    npt.assert_array_equal(choices.index, choosers.index)
    npt.assert_array_equal(sorted(choices.values), ['b', 'd', 'e', 'g', 'j'])


def test_unit_choice_not_enough(choosers, alternatives):
    probabilities = [0, 0, 0, 0, 0, 1, 0, 1, 0, 0]
    choices = lcm.unit_choice(
        choosers.index, alternatives.index, probabilities)
    npt.assert_array_equal(choices.index, choosers.index)
    assert choices.isnull().sum() == 3
    npt.assert_array_equal(sorted(choices[~choices.isnull()]), ['f', 'h'])


def test_unit_choice_none_available(choosers, alternatives):
    probabilities = [0] * len(alternatives)
    choices = lcm.unit_choice(
        choosers.index, alternatives.index, probabilities)
    npt.assert_array_equal(choices.index, choosers.index)
    assert choices.isnull().all()


def test_mnl_lcm(choosers, alternatives):
    model = lcm.MNLLocationChoiceModel(
        ['var3 != 15'], ['var2 != 14'], 'var2 + var1:var3', 5,
        name='Test LCM')
    loglik = model.fit(choosers, alternatives, choosers.thing_id)

    # hard to test things exactly because there's some randomness
    # involved, but can at least do a smoke test.
    assert len(loglik) == 3
    assert len(model.fit_results) == 2

    choices = model.predict(choosers, alternatives)

    npt.assert_array_equal(choices.index, choosers.index)
    assert choices.isin(alternatives.index).all()


def test_mnl_lcm_repeated_alts(choosers, alternatives):
    model = lcm.MNLLocationChoiceModel(
        ['var3 != 15'], ['var2 != 14'], 'var2 + var1:var3', 5,
        choice_column='thing_id', name='Test LCM')
    loglik = model.fit(choosers, alternatives, choosers.thing_id)

    # hard to test things exactly because there's some randomness
    # involved, but can at least do a smoke test.
    assert len(loglik) == 3
    assert len(model.fit_results) == 2

    repeated_index = alternatives.index.repeat([1, 2, 3, 2, 4, 3, 2, 1, 5, 8])
    repeated_alts = alternatives.loc[repeated_index].reset_index()

    choices = model.predict(choosers, repeated_alts)

    npt.assert_array_equal(choices.index, choosers.index)
    assert choices.isin(alternatives.index).all()
