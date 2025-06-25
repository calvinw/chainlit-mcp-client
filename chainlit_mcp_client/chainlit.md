### Live Demo Version (uses OPENROUTER\_API\_KEY)

[Chainit MCP Client](https://chainlit-mcp-client.mathplosion.com/)

### Version with Database Display (uses OPENROUTER\_API\_KEY)

[Chainit MCP Client With Database Display](https://calvinw.github.io/chainlit-mcp-client/iframe/index-chainlit-frame.html)

After you start put in your OPENROUTER\_API\_KEY, this will be saved in local storage for the browser. Next you may want to load up some MCP servers to work with.

Go to the wrench icon and you can load up local or remote MCPS with this Chainlit app. 

You can load up some remote MCPS at this point, here are the details:

### MCP Greet Server  
Type: SSE  
Name: mcp-greet   

ServerURL: 
https://mcp-greet.mcp.mathplosion.com/sse

### MCP Dolt Database Server  
Type: SSE  
Name: mcp-dolt-database  

ServerURL: 
https://bus-mgmt-databases.mcp.mathplosion.com/mcp-dolt-database/sse  

### MCP SEC 10ks Server 
Type: SSE  
Name: mcp-sec-10ks  

ServerURL: 
https://bus-mgmt-databases.mcp.mathplosion.com/mcp-sec-10ks/sse  

### MCP YFinance 10ks Server 
Type: SSE  
Name: mcp-yfinance-10ks  

ServerURL: 
https://bus-mgmt-databases.mcp.mathplosion.com/mcp-yfinance-10ks/sse  

With this dolt database MCP you can explore any dolt database in the format:

owner/database/branch

where 
 - `owner` is the database owner
 - `database` is the database name
 - `branch` is the branch of the database (typically its `main`)

For example `calvinw/coffee-shop/main` is [here](https://www.dolthub.com/repositories/calvinw/coffee-shop)

You will be able only be able to query it in *view* only mode unless you pass it a dolt api token.

## Tools Available 

Here are the Dolt database explorer tools available. You can also ask the LLM to give them to you:


| Tool Name | Description |
|-----------|-------------|
| `read_query` | Execute SQL read queries safely on the Dolt database. Takes a SQL query and database string as parameters. |
| `write_query` | Execute write operations (INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, RENAME) on the Dolt database. Handles polling for asynchronous operations. Requires an API token in addition to SQL query and database string. |
| `list_tables` | List the BASE tables in the database (excluding views). Only requires the database string parameter. |
| `describe_table` | Describe the structure of a specific table. Handles table names that require quoting automatically. Takes table name and database string as parameters. |
| `list_views` | List the views in the database. Only requires the database string parameter. |
| `describe_view` | Show the CREATE VIEW statement for a specific view. Takes view name and database string as parameters. |

These tools allow you to explore and interact with Dolt databases - from basic schema exploration with `list_tables` and `describe_table`, to querying data with `read_query`, and making changes with `write_query`. The write operations require an API token for authentication, while read operations do not.


## Databases You Can Try 

### BusMgmtBenchmarks (calvinw/BusMgmtBenchmarks/main)

The financial BusMgmtBenchmarks database is:    
```bash
calvinw/BusMgmtBenchmarks/main
```
[DoltHub version](https://www.dolthub.com/repositories/calvinw/BusMgmtBenchmarks) | [Schema documentation](https://www.dolthub.com/repositories/calvinw/BusMgmtBenchmarks/schema/main)

This is the BusMgmtBenchmarks project is described [here](https://www.dolthub.com/repositories/calvinw/BusMgmtBenchmarks)

### Retail Orders (calvinw/retail-orders/main)

A simple retail-orders example is here:
```bash
calvinw/retail-orders/main
```
[DoltHub version](https://www.dolthub.com/repositories/calvinw/retail-orders) | [Schema documentation](https://www.dolthub.com/repositories/calvinw/retail-orders/schema/main)

### Engagement Marketing (calvinw/engagement/main)

An example of an engagment marketing database:
```bash
calvinw/engagement/main
```
[DoltHub version](https://www.dolthub.com/repositories/calvinw/engagement) | [Schema documentation](https://www.dolthub.com/repositories/calvinw/engagement/schema/main)

### Sakila DVD Rental Store (calvinw/sakila/main)

Dolt version of well known sakila database:

```bash
calvinw/sakila/main
```
[DoltHub version](https://www.dolthub.com/repositories/calvinw/sakila) | [Schema documentation](https://www.dolthub.com/repositories/calvinw/sakila/schema/main)


## Prompts to Try 

- Can you tell me what tables are in the database?
- Can you describe the schema of the products table?
- Can you summarize the database and tell me what the tables are for?

### Example of Coffee Shop database (calvinw/coffee-shop/main)  

#### products Table

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

#### Orders Table

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

