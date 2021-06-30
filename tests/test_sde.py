import os
from sde import edit_json

# change dir to tests directory to make relative paths possible
os.chdir(os.path.dirname(os.path.realpath(__file__)))


def test_json_edit():
    """Test passing a yml file as repo argument."""
    file = os.path.dirname(os.path.abspath(__file__)) + '/test.json'
    edit_json('age', 32, file)

    import json
    with open(file) as json_file:
        data = json.load(json_file)
        assert data['age'] == 32

    edit_json('age', 31, file)

    import json
    with open(file) as json_file:
        data = json.load(json_file)
        assert data['age'] == 31