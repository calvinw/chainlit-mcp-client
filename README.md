# MCP Sqlite Server 

## Coffee Shop Database

This database is [here](https://www.dolthub.com/repositories/calvinw/coffee-shop)

You will be able only be able to query it in *view* only mode.

You can see the structure of the database [here](https://www.dolthub.com/repositories/calvinw/coffee-shop/schema/main)

To set the DoltMcpServer to use this database go to the DoltMcpServer settings and adjust like this:

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

Here are the tables since they are so small

### Products Table

| Product ID | Name               | Category | Price | Description                                                   | In Stock |
|------------|-------------------|----------|-------|---------------------------------------------------------------|----------|
| 1          | Espresso           | Coffee   | $2.50 | Strong black coffee made by forcing steam through ground coffee beans | Yes |
| 2          | Cappuccino         | Coffee   | $3.50 | Espresso with steamed milk foam                               | Yes |
| 3          | Latte              | Coffee   | $3.75 | Espresso with steamed milk                                    | Yes |
| 4          | Americano          | Coffee   | $2.75 | Espresso with hot water                                       | Yes |
| 5          | Matcha Latte       | Tea      | $4.25 | Green tea powder with steamed milk                            | Yes |
| 6          | Earl Grey          | Tea      | $2.50 | Black tea flavored with bergamot                              | Yes |
| 7          | Chocolate Croissant| Pastry   | $3.25 | Buttery croissant with chocolate filling                      | Yes |
| 8          | Blueberry Muffin   | Pastry   | $2.95 | Moist muffin with fresh blueberries                           | Yes |
| 9          | Iced Coffee        | Coffee   | $3.25 | Chilled coffee served with ice                                | Yes |
| 10         | Chai Latte         | Tea      | $3.95 | Spiced tea with steamed milk                                  | Yes |

### Orders Table

| Order ID | Product ID | Customer Name  | Quantity | Order Date           | Completed |
|----------|------------|----------------|----------|----------------------|-----------|
| 1        | 2          | John Smith     | 1        | 2025-04-13 08:15:00  | Yes       |
| 2        | 7          | John Smith     | 1        | 2025-04-13 08:15:00  | Yes       |
| 3        | 5          | Emma Johnson   | 1        | 2025-04-13 09:22:00  | Yes       |
| 4        | 10         | Michael Brown  | 2        | 2025-04-13 10:05:00  | Yes       |
| 5        | 1          | Sarah Davis    | 1        | 2025-04-13 10:30:00  | Yes       |
| 6        | 3          | David Wilson   | 1        | 2025-04-13 11:15:00  | No        |
| 7        | 8          | David Wilson   | 2        | 2025-04-13 11:15:00  | No        |
| 8        | 9          | Jennifer Lee   | 1        | 2025-04-13 11:42:00  | No        |
| 9        | 4          | Robert Taylor  | 1        | 2025-04-13 12:10:00  | No        |
| 10       | 6          | Lisa Anderson  | 3        | 2025-04-13 12:25:00  | No        |


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

