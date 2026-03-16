# BaytFactory

Smart-home product-line engineering studio for:
- editing a feature model,
- deriving a valid product configuration with SAT,
- editing annotated source code,
- generating a runnable variant,
- launching it in Home Assistant.

![BaytFactory overview](docs/screenshots/baytfactory-home.png)

## What It Does

BaytFactory is a Streamlit application that combines four workflows in one place:

1. `Feature Model (FM)`
   Edit the feature hierarchy, mandatory/optional flags, `xor` / `or` groups, and cross-tree constraints.

2. `Variant Derivation`
   Select features, let the SAT solver infer required ones, and lock incompatible choices.

3. `Code Explorer`
   Open a project workspace, a generated variant, or any local folder in a Monaco-based editor with SPL annotations.

4. `Variant Runtime`
   Generate a derived variant and launch it in Home Assistant for validation.

## Screenshot Tutorial

### 1. Open the Studio

Run the app and open the local URL:

```bash
streamlit run baytfactory_spl.py
```

You will land on the main studio with three workspaces:
- `Feature Model (FM)`
- `Variant Derivation`
- `Code Explorer`

### 2. Load a Project

BaytFactory supports two inputs:

- `Workspace folder`
  Point directly to a local project directory.
- `ZIP upload`
  Upload one archive containing source code and one `*.fm.json`.

Expected contents:

```text
project/
├─ src/
│  ├─ module_a.py
│  └─ ...
└─ smart_home.fm.json
```

The tool automatically detects:
- the feature model file,
- the source directory,
- the generated variants workspace.

### 3. Edit the Feature Model

Go to `Feature Model (FM)`.

Use:
- `FM Preview` to inspect the feature tree and constraints,
- `FM Editor` to modify:
  - feature key and label,
  - `mandatory` state,
  - `xor` / `or` group type,
  - cross-tree `requires` / `excludes`,
  - child features.

Typical usage:

1. open a feature in the tree,
2. edit its properties,
3. save the draft model,
4. validate the resulting FM.

### 4. Derive a Variant

Go to `Variant Derivation`.

The configurator now supports:
- automatic inference of required features,
- automatic parent selection,
- locking of incompatible choices:
  - `xor` siblings,
  - `excludes` conflicts,
- solver explanations for inferred features.

Typical flow:

1. check the features you want manually,
2. let the solver infer required dependencies,
3. inspect `Solver Insight`,
4. verify the resolved feature set,
5. generate the variant.

### 5. Explore and Edit Code

Go to `Code Explorer`.

You can open:
- the project workspace,
- a generated variant,
- any local folder path.

The editor provides:
- Monaco-based code editing,
- SPL annotation awareness for `#if[...] ... #endif`,
- file tree browsing,
- save / rename / delete actions,
- quick switching between project and variant workspaces.

Supported annotation style:

```txt
#if[Alarm && (WiFi || Zigbee)]
... code ...
#endif
```

### 6. Generate and Deploy

At the bottom of `Variant Derivation`, the `Variant Runtime` section gives the final workflow:

1. `Generate Variant`
2. `Deploy on Home Assistant`

The generated variant is stored under:

```text
spl-smarthome-generated-variants/<variant_name>/
```

BaytFactory also exports:

```text
spl-smarthome-generated-variants/<variant_name>/social_rules.json
```

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r "requirements (2).txt"
pip install "python-sat[pblib,aiger]"
```

Then run:

```bash
streamlit run baytfactory_spl.py
```

## Requirements

- Python 3.10+
- `streamlit`
- `python-dotenv`
- `python-sat[pblib,aiger]`

Optional for Home Assistant runtime:

- `homeassistant`

Example:

```bash
python3 -m venv spl-smarthome-generated-variants/.env
spl-smarthome-generated-variants/.env/bin/pip install homeassistant
```

## Feature Model Format

Minimal example:

```json
{
  "features": [
    {
      "key": "Root",
      "name": "SmartHome",
      "mandatory": true,
      "children": [
        {
          "key": "Alarm",
          "name": "Alarm",
          "group": "xor",
          "children": [
            { "key": "Siren", "name": "Siren" },
            { "key": "Silent", "name": "Silent Alarm" }
          ]
        },
        { "key": "WiFi", "name": "WiFi" },
        { "key": "SmartThermostat", "name": "Smart Thermostat" }
      ]
    }
  ],
  "constraints": [
    { "type": "requires", "source": "SmartThermostat", "target": "AirConditioner" },
    { "type": "excludes", "source": "Siren", "target": "Silent" }
  ]
}
```

Notes:
- `features` contains one root node.
- `group` applies to the node children.
- supported cross-tree relations are `requires` and `excludes`.

## Source Annotation Rules

BaytFactory derives code by evaluating `#if[...]` guards against the resolved configuration.

Supported operators:
- `&&`
- `||`
- `!`

Example:

```txt
#if[Door_SensorCamera && WiFi]
...
#endif
```

## Home Assistant

BaytFactory can launch Home Assistant against a generated variant directory.

Shared HA environment:

```text
spl-smarthome-generated-variants/.env/
```

Variant config directory:

```text
spl-smarthome-generated-variants/<variant_name>/
```

## Troubleshooting

- `ZIP must contain .fm.json and source code`
  The uploaded archive does not contain a valid FM file and a detectable source directory.

- `Invalid configuration`
  A `requires`, `excludes`, `xor`, `or`, or parent/child rule is violated.

- Home Assistant cannot start
  Check the shared HA environment under `spl-smarthome-generated-variants/.env`.

- A feature is locked in the configurator
  It is currently blocked by:
  - an active `xor` choice,
  - or an `excludes` constraint.

## Repository Structure

```text
baytfactory-tool/
├─ baytfactory_spl.py
├─ sat_interactive.py
├─ annotated_monaco.py
├─ components/
├─ docs/
│  └─ screenshots/
├─ spl-smarthome-generated-variants/
└─ README.md
```

## Current Entry Point

Use:

```bash
streamlit run baytfactory_spl.py
```

`baytfactory_spl.py` is the current application entrypoint for this repository.
