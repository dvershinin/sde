import os
import subprocess

from sde import edit_file, read_file

# change dir to tests directory to make relative paths possible
os.chdir(os.path.dirname(os.path.realpath(__file__)))


def test_json_edit():
    file = os.path.dirname(os.path.abspath(__file__)) + '/test.json'
    edit_file('age', 32, file, 'JSON')

    import json
    with open(file) as json_file:
        data = json.load(json_file)
        assert data['age'] == 32

    edit_file('age', 31, file, 'JSON')

    import json
    with open(file) as json_file:
        data = json.load(json_file)
        assert data['age'] == 31


def test_yaml_edit():
    file = os.path.dirname(os.path.abspath(__file__)) + '/test.yaml'
    edit_file('age', 32, file, 'YAML')

    import yaml
    with open(file) as yaml_file:
        data = yaml.safe_load(yaml_file)
        assert data['age'] == 32

    edit_file('age', 31, file, 'YAML')

    import yaml
    with open(file) as yaml_file:
        data = yaml.safe_load(yaml_file)
        assert data['age'] == 31


def test_cli_json():
    # different filename to facilitate parallel tests
    file = os.path.dirname(os.path.abspath(__file__)) + '/test-cli.json'

    process = subprocess.Popen(
        ['sde', "extra.sex", "female", file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.communicate()

    data = read_file(file, 'JSON')

    assert data['extra']['sex'] == 'female'

    process = subprocess.Popen(
        ['sde', "extra.sex", "male", file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.communicate()

    data = read_file(file, 'JSON')

    assert data['extra']['sex'] == 'male'

    process = subprocess.Popen(
        ['sde', "extra.sex", "true", file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.communicate()

    data = read_file(file, 'JSON')

    assert data['extra']['sex'] is True

    process = subprocess.Popen(
        ['sde', "-s", "extra.sex", "true", file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    process.communicate()

    data = read_file(file, 'JSON')

    assert data['extra']['sex'] == 'true'
