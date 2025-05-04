# MCP Dolt Server

Click on the [Chainlit MCP client](https://calvinw.github.io/chainlit-mcp-client/iframe/index-chainlit-frame.html)

and you will be able to set up and use the MCP Dolt Server to work with any dolt database. Even if you do not own the database, you can still view it with this tool. If you additionally have a dolt api-token you can edit the database if you own it or are a collaborator on it.

## Coffee Shop Database

This database is [here](https://www.dolthub.com/repositories/calvinw/coffee-shop)

You will be able only be able to query it in *view* only mode.

You can see the structure of the database [here](https://www.dolthub.com/repositories/calvinw/coffee-shop/schema/main)

To set the DoltMcpServer to use this database go to the DoltMcpServer settings (click on the plug icon) and set it up like this:

### Name 
```bash
DoltMcpServer
```
### Command
```bash
uvx bus-mgmt-dolt-mcp-server --db calvinw/coffee-shop/main
```
The parts to the --db are the user/database/branch where the user is the name of the owner of the databse, not the user of the MCP server. Then the database is the name of the database and the last part is the branch.

Here are the available tools

| Tool Name                 | Description                                                                                                                                |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| `export_views_statements` | Export DROP VIEW and CREATE VIEW statements for all views. First outputs all DROP VIEW IF EXISTS statements, then outputs the CREATE VIEW statements. |
| `read_query`              | Execute SQL read queries safely on the Dolt database                                                                                       |
| `write_query`             | Execute write operations (INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, RENAME) on the Dolt database. Handles polling for asynchronous operations. |
| `list_tables`             | List the BASE tables in the database (excluding views)                                                                                     |
| `describe_table`          | Describe the structure of a specific table. Handles table names that require quoting (e.g., containing spaces) automatically.                |
| `download_table_csv`      | Downloads the content of a specific table as CSV text using the DoltHub API. Handles table names that require quoting automatically.         |
| `list_views`              | List the views in the database                                                                                                             |
| `describe_view`           | Show the CREATE VIEW statement for a specific view. Handles view names that require quoting (e.g., containing spaces) automatically.         |
| `create_view`             | Create a new view in the database using the provided SELECT query. Handles view names that require quoting (e.g., containing spaces) automatically. Uses the write_query tool for execution. |
| `drop_view`               | Drop a view from the database. Handles view names that require quoting (e.g., containing spaces) automatically. Uses the write_query tool for execution. |
| `drop_all_views`          | Drop all views from the database by listing all views and invoking drop_view for each. If a drop fails due to a timeout, the function will retry the drop once. |
| `greet`                   |                                                                                                                                            |
| `get_current_database`    | Return the currently configured database connection string in user/database/branch format.                                                 |
| `set_current_database`    | Set the active database connection string. Expects format: user/database/branch.                                                           |
## Prompts to Try 

> Can you tell me what tables are in the database?

> Can you describe the schema of the products table?

## Example Chat Logs About Database

Here is an [Example Chat Log](https://calvinw.github.io/chainlit-mcp-client/example_chat_with_sqlite_mcp_server.html) about the database

Here is an example [Show SQL and Tables Info](https://calvinw.github.io/chainlit-mcp-client/list_all_sql_and_table_state.html) showing that the LLM can list the SQL commands it performs and the state of the tables afterwards. 

Here is an example of making a new table and moving information to that table
[Adding Customer Table](https://calvinw.github.io/chainlit-mcp-client/adding_customer_table.html)

## Business Managment Benchmarks 

This is the BusMgmtBenchmarks database with the details 
given [here](https://www.dolthub.com/repositories/calvinw/BusMgmtBenchmarks)

You will be able only be able to query it in *view* only mode.

You have to set the DoltMcpServer to access this database like this

Click on the plug icon and enter

### Name 
```bash
DoltMcpServer
```
### Command
```bash
uvx bus-mgmt-dolt-mcp-server --db calvinw/BusMgmtBenchmarks/main 
```

You can see the structure of the database [here](https://www.dolthub.com/repositories/calvinw/BusMgmtBenchmarks/schema/main)

