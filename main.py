import os
from dotenv import load_dotenv
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as tck


# Load environment variables
BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, ".env"))

SQL_DRIVER = "{MySQL ODBC 8.0 ANSI Driver}"
SQL_SERVER = "localhost"
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

# Create connection to MySQL database
cnxn = pyodbc.connect(
    f"DRIVER={SQL_DRIVER};SERVER={SQL_SERVER};UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
)

# Create a cursor from the connection
cursor = cnxn.cursor()

cursor.execute("USE northwind;")


# --------------------------------------------------------------------
# Sale data across countries

# Retrieve data
cursor.execute(
    """
SELECT OrderDetails.UnitPrice, OrderDetails.Quantity, OrderDetails.Discount, Orders.ShipCountry 
FROM OrderDetails 
JOIN Orders ON OrderDetails.OrderID = Orders.OrderID 
ORDER BY ShipCountry;
"""
)

rows = cursor.fetchall()

column_names = [column[0] for column in cursor.description]

# Convert to dataframe and calculate total sale
sale_df = pd.DataFrame.from_records(
    data=rows,
    columns=column_names,
    coerce_float=True,
)

# Consider sorting by total revenue instead of country name
sale_df["TotalSale"] = sale_df.UnitPrice * sale_df.Quantity * (1 - sale_df.Discount)
total_sale_per_country = sale_df.groupby("ShipCountry")["TotalSale"].sum().to_frame()

# Plot data
fig, ax = plt.subplots()

ax.bar(total_sale_per_country.index, total_sale_per_country.TotalSale)

plt.xticks(rotation=90)

ax.get_yaxis().set_major_formatter(tck.FuncFormatter(lambda x, p: format(int(x), ",")))
plt.ylabel("Revenue [$]")

plt.subplots_adjust(bottom=0.25, left=0.15)
plt.title("Total revenue across different countries")

plt.show()


# --------------------------------------------------------------------
#

# Close connection
cnxn.close()
