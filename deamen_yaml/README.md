# deamen_yaml

`deamen_yaml` is a Python module for working with YAML files. It provides a simple and intuitive interface for reading, writing, and manipulating YAML data.

## Features

- **IndentDumper**: IndentDumper is a custom YAML dumper class designed to ensure proper indentation of sequences under mappings when writing YAML data. This class extends the default yaml.Dumper provided by the PyYAML library.

## Installation

You can install `deamen_yaml` using pip:

```sh
pip install deamen_yaml
```

## Usage

### IndentDumper

```python
import yaml
from deamen_yaml.utils import IndentDumper

data = {
    'name': 'John Doe',
    'age': 30,
    'city': 'New York',
    'hobbies': ['reading', 'hiking', 'coding']
}

with open('output.yaml', 'w') as f:
    yaml.dump(
        data,
        f,
        Dumper=IndentDumper,
        default_flow_style=False,
        sort_keys=False,
        indent=2
    )
```

### Example

Given the following data:

```python
data = {
    'name': 'John Doe',
    'age': 30,
    'city': 'New York',
    'hobbies': ['reading', 'hiking', 'coding']
}
```

Using `IndentDumper` to write this data to a YAML file will produce:

```yaml
name: John Doe
age: 30
city: New York
hobbies:
  - reading
  - hiking
  - coding
```

