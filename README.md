# sde

`sde` is not `sed`. It's a structured data editor for CLI.

## Why?

Many people asked for a simple JSON in-place editing and `jq` was the solution:

* [Modify a key-value in a json using jq in-place](https://stackoverflow.com/questions/42716734/modify-a-key-value-in-a-json-using-jq-in-place)
* [How to modify a key's value in a JSON file from command line](https://stackoverflow.com/questions/43292243/how-to-modify-a-keys-value-in-a-json-file-from-command-line)

```bash
jq '.address = "abcde"' test.json|sponge test.json
```
    
Does this seem readable or elegant to you?

`sde` is not a substitue for `jq` or `sed`.

It allows *simple* in-place JSON value changes, for *simple* data.

```json
{
   "name":"John",
   "age":31,
   "city":"New York",
   "extra": {
       "sex": "male"
   }
}
```

### Modify data

```bash
sde name Jack data.json
sde extra.sex female data.json
sde pools.0.pass secret data.json
```

```bash
echo $json | sde name Jack
```

### Query simple data

```bash
sdg name data.json
```