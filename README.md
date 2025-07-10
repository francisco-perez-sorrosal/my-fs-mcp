# My MCP for Filesystem Access for Claude

## References

[Claude Desktop Extensions](https://www.anthropic.com/engineering/desktop-extensions)

## TL;DR

Create dxt bundle with:

```sh
make
```

Drag `dxt-package/my-fs-mcp.dxt` to `Claude/Settings.../Extensions` to install bundle.

## Dev

### Requirements

- `pixi`
- `uv`

### Init the dxt

Init dxt project with a manifest

```sh
npx @anthropic-ai/dxt init --yes
```

**Note** When creating the manifest, in the `mpc_config` section, put the full path to the python interpreter ->  `"command": "/Users/fperez/.pyenv/shims/python"`

### Bundle Python libs and Package Project

```sh
pixi install
pixi run bundle
pixi run pack
```

The output `.dxt` file is created on the dxt-package directory. Once the `.dxt` file is created you can drag and drop it to Claude (in the `Settings/Extensions` section.)

### Testing it

Run server with:

```sh
pixi test
```

Then open the inspector:

```sh
DANGEROUSLY_OMIT_AUTH=true npx @modelcontextprotocol/inspector
```

And then:

- go to the URL specified
- select stdio as connection method
- put `pixi` in `Command` input box
- put `run python server/main.py --debug` in the `Arguments` input box
- click connect
- go to tools and list them


**NOTE** For testing the server as extension is run when added to Claude try:

```sh
PYTHONPATH="/Users/fperez/Library/Application Support/Claude/Claude Extensions/local.dxt.francisco-perez-sorrosal.my-fs-mcp/server/lib" python /Users/fperez/Library/Application\ Support/Claude/Claude\ Extensions/local.dxt.francisco-perez-sorrosal.my-fs-mcp/server/main.py --debug --workspace=${HOME}/Documents
```
