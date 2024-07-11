# IUS Time

**Usage**:

```console
$ ius [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `end`: End active tasks.
* `list`: List tasks, with an optional time filter.
* `start`: Start a new task.
* `total`: Sum the amount of time spent on your tasks.

## `ius end`

End active tasks.

**Usage**:

```console
$ ius end [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `all`: End all active tasks.
* `last`: End the last task that was started.
* `task`: Specify the name of the task to end.

### `ius end all`

End all active tasks.

**Usage**:

```console
$ ius end all [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `ius end last`

End the last task that was started.

**Usage**:

```console
$ ius end last [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `ius end task`

Specify the name of the task to end.

**Usage**:

```console
$ ius end task [OPTIONS] TASK_NAME
```

**Arguments**:

* `TASK_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `ius list`

List tasks, with an optional time filter.

**Usage**:

```console
$ ius list [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `active`: List only active tasks.
* `all`: List all tasks in the database.
* `complete`: List only completed tasks.

### `ius list active`

List only active tasks.

**Usage**:

```console
$ ius list active [OPTIONS]
```

**Options**:

* `-f, --filter [day|week|month|quarter|semiannual|year|none]`: When applied, limits list output to tasks started within the filter window.  [default: month]
* `--help`: Show this message and exit.

### `ius list all`

List all tasks in the database.

**Usage**:

```console
$ ius list all [OPTIONS]
```

**Options**:

* `-f, --filter [day|week|month|quarter|semiannual|year|none]`: When applied, limits list output to tasks started within the filter window.  [default: month]
* `--help`: Show this message and exit.

### `ius list complete`

List only completed tasks.

**Usage**:

```console
$ ius list complete [OPTIONS]
```

**Options**:

* `-f, --filter [day|week|month|quarter|semiannual|year|none]`: When applied, limits list output to tasks started within the filter window.  [default: month]
* `--help`: Show this message and exit.

## `ius start`

Start a new task.

**Usage**:

```console
$ ius start [OPTIONS] TASK_NAME
```

**Arguments**:

* `TASK_NAME`: [required]

**Options**:

* `-c, --category TEXT`: [default: Misc]
* `--help`: Show this message and exit.

## `ius total`

Sum the amount of time spent on your tasks. Only calculated for completed tasks

**Usage**:

```console
$ ius total [OPTIONS]
```

**Options**:

* `-f, --filter [day|week|month|quarter|semiannual|year|none]`: When applied, limits list output to tasks started within the filter window.  [default: month]
* `-c, --category TEXT`
* `--help`: Show this message and exit.
