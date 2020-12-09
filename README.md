# Concourse resource for Fossil

This is a new Python implementation of the [Fossil-Repo from Avalos](https://fossil.avalos.me/fossil-concourse/doc/trunk/index.md) for private Fossil repository.

Concourse resource for [Fossil](https://fossil-scm.org) repos, so you can integrate cool continuous thing-doing in your Fossil project. For more information about installing and using Concourse and writing pipelines, please visit the [docs](https://concourse-ci.org/docs.html). 


## Pre-requisites
+ Latest* Fossil compiled with JSON support.
+ Fossil server running in HTTP or CGI.
+ `HTTP_AUTHENTICATION` enabled in repo Access settings (only if it is private).


## Resource type configuration

```
resource_types:
  - name: fossil-resource
    type: docker-image
    source:
      repository: stenderg/concourse-fossil-resource
      tag: latest
```

## Source configuration

+ `url`: the URL of the Fossil repository **(required)**.
+ `branch`: the branch to monitor and pull from Concourse **(required)**.
+ `user`: Fossil repo user with read privileges _(required if repo is private)_.
+ `password`: password for the Fossil repo user _(required if repo is private)_.

## Behavior

### `check`. Poll commits on branch

The resource will fetch the `/json/timeline` endpoint from the specified `url`, and it will return a `ref` value containing the ID of the commit.

### `in`. Pull commit from repo

The `ref` from the `check` step will be used as the input. The resource will download a tarball from the `/tarball/{ref}` endpoint and extract it into the destination directory.

### `out`. Not implemented

This resource doesn't allow making pushes yet.

## Example

```
resource_types:
  - name: fossil-resource
    type: docker-image
    source:
      repository: stenderg/concourse-fossil-resource
      tag: latest

resources:
  - name: fossil
    type: fossil-resource
    source:
      url: https://fossil.avalos.me/fossil-concourse
      branch: trunk

jobs:
  - name: do-something
    serial: true
    plan:
      - get: fossil
        trigger: true
      - task: build
        config:
          platform: linux
          image_resource:
            type: docker-image
            source:
              repository: alpine
              tag: edge
          inputs:
            - name: fossil
              path: .
          run:
            path: ls
            args:
              - -la
```

## Testing
...


## License

```
Copyright (C) 2020  Gordon Stender

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```