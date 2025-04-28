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

