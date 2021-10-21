import os
from sde import edit_file

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
