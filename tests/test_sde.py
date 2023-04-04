import os
import subprocess
import json
import yaml
from sde import edit_file, normalize_val, read_file

# change dir to tests directory to make relative paths possible
os.chdir(os.path.dirname(os.path.realpath(__file__)))


def test_json_edit():
    """
    Test JSON editing.
    Note that in the app, actual data is normalized first from argparse strings,
    so we make use of normalize_val
    """
    file = os.path.dirname(os.path.abspath(__file__)) + '/test.json'
    edit_file('age', normalize_val('31'), file, 'JSON')
    edit_file('balance', normalize_val('0'), file, 'JSON')

    with open(file) as json_file:
        data = json.load(json_file)
        assert data['age'] == 31
        assert data['balance'] == 0

    edit_file('age', normalize_val('32'), file, 'JSON')
    edit_file('balance', normalize_val('-100.25'), file, 'JSON')

    with open(file) as json_file:
        data = json.load(json_file)
        assert data['age'] == 32
        assert data['balance'] == -100.25


def test_yaml_edit():
    """
    Test YAML editing.
    Note that in the app, actual data is normalized first from argparse strings,
    so we make use of normalize_val
    """
    file = os.path.dirname(os.path.abspath(__file__)) + '/test.yaml'
    edit_file('age', normalize_val('31'), file, 'YAML')
    edit_file('balance', normalize_val('0'), file, 'YAML')

    with open(file) as yaml_file:
        data = yaml.safe_load(yaml_file)
        assert data['age'] == 31
        assert data['balance'] == 0

    edit_file('age', normalize_val('32'), file, 'YAML')
    edit_file('balance', normalize_val('-100.25'), file, 'YAML')

    with open(file) as yaml_file:
        data = yaml.safe_load(yaml_file)
        assert data['age'] == 32
        assert data['balance'] == -100.25


def test_cli_json():
    # different filename to facilitate parallel tests
    file = os.path.dirname(os.path.abspath(__file__)) + '/test-cli.json'

    process = subprocess.Popen(
        ['sde', "extra.gender", "female", file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.communicate()

    data = read_file(file, 'JSON')

    assert data['extra']['gender'] == 'female'

    process = subprocess.Popen(
        ['sde', "extra.gender", "male", file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.communicate()

    data = read_file(file, 'JSON')

    assert data['extra']['gender'] == 'male'

    process = subprocess.Popen(
        ['sde', "extra.gender", "null", file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.communicate()

    data = read_file(file, 'JSON')

    assert data['extra']['gender'] is None

    process = subprocess.Popen(
        ['sde', "-s", "extra.registered", "true", file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.communicate()

    data = read_file(file, 'JSON')

    assert data['extra']['registered'] == 'true'

    process = subprocess.Popen(
        ['sde', "-s", "extra.registered", "true", file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.communicate()

    data = read_file(file, 'JSON')

    assert data['extra']['registered'] == 'true'
