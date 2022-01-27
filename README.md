# sde

[![PyPI version](https://badge.fury.io/py/sde.svg)](https://badge.fury.io/py/sde)

`sde` is not `sed`. It's a structured data editor for CLI.

## Why?

Many people asked for a simple JSON in-place editing and `jq` was the solution:

* [Modify a key-value in a json using jq in-place](https://stackoverflow.com/questions/42716734/modify-a-key-value-in-a-json-using-jq-in-place)
* [How to modify a key's value in a JSON file from command line](https://stackoverflow.com/questions/43292243/how-to-modify-a-keys-value-in-a-json-file-from-command-line)

```bash
jq '.address = "abcde"' test.json|sponge test.json
```
    
Does this seem readable or elegant to you?

`sde` is not a substitute for `jq` or `sed`.

It allows *simple* in-place JSON/YAML value changes, for *simple* data.

### Sample JSON

```json
{
   "name":"John",
   "age":31,
   "city":"New York",
   "extra": {
       "gender": null
   }
}
```

### Sample YAML

```yaml
database:
  user: example
  password: secret
```

### Modify data

```bash
sde name Jack data.json
sde extra.gender male data.json
sde database.user john data.yml
```

It is possible to modify data in arrays, e.g.:

```json
{
    "users": [
        {
            "username": "foo", 
            "enabled": true
        },
        {
            "username": "bar", 
            "enabled": true
        }      
    ],
}
```

Set the first user's `enabled` property to `false`:

```bash
sde users.0.enabled false data.json
```

## Installation for CentOS/RHEL 7, 8 or Amazon Linux 2

```bash
sudo yum -y install https://extras.getpagespeed.com/release-latest.rpm
sudo yum -y install sde
```
   
## Installation for other systems

Installing with `pip` is easiest:

```bash
pip install sde
```

## Notes

Quoting is avoided for `null`, `true`, `false`, and numeric values.
To ensure that a given value is quoted, use `-s` (or `--string`) option:

```bash
sde -s key null file.json
```

If you must *edit* the file, by ensuring to update only the existing key, use `-e` (`--must-exist`)
option. The program will exit without adding the key which doesn't exist.

```bash
sde -e key val file.json
```

## TODO

### Work with stdin

```bash
echo $json | sde name Jack
```

### Query simple data

```bash
sdg name data.json
```