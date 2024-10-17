import matplotlib.pyplot as plt
import glob
import pandas as pd
from functools import reduce
plt.rcParams['text.usetex'] = True
# Set the font family to serif (you can change to 'sans-serif', etc.)
plt.rcParams['font.family'] = 'serif'
# Set the font size for labels, titles, etc.
plt.rcParams['font.size'] = 40
plt.rcParams['axes.labelsize'] = 14    # Set the font size for axis labels
plt.rcParams['xtick.labelsize'] = 20   # Set the font size for x-tick labels
plt.rcParams['ytick.labelsize'] = 20   # Set the font size for y-tick labels
plt.rcParams['legend.fontsize'] = 20   # Set the font size for the legend

cov_seq_csvs = glob.glob("cov_seq.csv.mbt_rand_trial-*.tar.gz")
dfs = []
min_length = 0
for csv_file in cov_seq_csvs:
    df = pd.read_csv(open(csv_file), index_col=0)
    print(df)
    na_values = {}
    for column in df.columns:
        na_values[column] = df[column].max()
    df = df.fillna(na_values)
    print(df)
    dfs.append(df)
    if min_length == 0:
        min_length = len(df.index)
    else:
        min_length = min(len(df.index), min_length)

print("min_length: ", min_length)
result = reduce(lambda a, b: a[:min_length].add(
    b[:min_length], fill_value=0), dfs)

result = result / len(dfs)
print(result)

result.to_csv("average_cov.csv")


# Sample data for multiple lines
x = range(1, min_length + 1)
y1 = result["./random_myth_CryptoPunksMarket.log-random"]
y2 = result["./mbt_myth_CryptoPunksMarket.log-mbt"]


# Create the line chart with multiple lines
plt.plot(x, y2, marker='x', linestyle='--', color='r', label='Mythril-SMCon')
plt.plot(x, y1, marker='o', linestyle='-', color='b', label='Mythril-Random')

# Add titles and labels
# plt.title('Line Chart with Multiple Lines')
# plt.xlabel('Number of function call sequences used')
# plt.ylabel('Opcode Coverage (%)')

# Show legend
plt.legend()

# Display the chart
# plt.show()
plt.tight_layout()
plt.savefig("CryptoPunksMarket.pdf")

plt.close()

# Sample data for multiple lines
x = range(1, min_length + 1)
y1 = result["./random_myth_GameChannel.log-random"]
y2 = result["./mbt_myth_GameChannel.log-mbt"]


# Create the line chart with multiple lines
plt.plot(x, y2, marker='x', linestyle='--', color='r', label='Mythril-SMCon')
plt.plot(x, y1, marker='o', linestyle='-', color='b', label='Mythril-Random')

# Add titles and labels
# plt.title('Line Chart with Multiple Lines')
# plt.xlabel('Number of function call sequences used')
# plt.ylabel('Opcode Coverage (%)')

# Show legend
plt.legend()

# Display the chart
# plt.show()
plt.tight_layout()
plt.savefig("GameChannel.pdf")


plt.close()

# Sample data for multiple lines
x = range(1, min_length + 1)
y1 = result["./random_myth_MoonCatRescue.log-random"]
y2 = result["./mbt_myth_MoonCatRescue.log-mbt"]


# Create the line chart with multiple lines
plt.plot(x, y2, marker='x', linestyle='--', color='r', label='Mythril-SMCon')
plt.plot(x, y1, marker='o', linestyle='-', color='b', label='Mythril-Random')

# Add titles and labels
# plt.title('Line Chart with Multiple Lines')
# plt.xlabel('Number of function call sequences used')
# plt.ylabel('Opcode Coverage (%)')

# Show legend
plt.legend()

# Display the chart
# plt.show()
plt.tight_layout()
plt.savefig("MoonCatRescue.pdf")


plt.close()

# Sample data for multiple lines
x = range(1, min_length + 1)
y1 = result["./random_myth_RpsGame.log-random"]
y2 = result["./mbt_myth_RpsGame.log-mbt"]


# Create the line chart with multiple lines
plt.plot(x, y2, marker='x', linestyle='--', color='r', label='Mythril-SMCon')
plt.plot(x, y1, marker='o', linestyle='-', color='b', label='Mythril-Random')

# Add titles and labels
# plt.title('Line Chart with Multiple Lines')
# plt.xlabel('Number of function call sequences used')
# plt.ylabel('Opcode Coverage (%)')

# Show legend
plt.legend()

# Display the chart
# plt.show()
plt.tight_layout()
plt.savefig("RpsGame.pdf")


plt.close()

# Sample data for multiple lines
x = range(1, min_length + 1)
y1 = result["./random_myth_SaleClockAuction.log-random"]
y2 = result["./mbt_myth_SaleClockAuction.log-mbt"]


# Create the line chart with multiple lines
plt.plot(x, y2, marker='x', linestyle='--', color='r', label='Mythril-SMCon')
plt.plot(x, y1, marker='o', linestyle='-', color='b', label='Mythril-Random')

# Add titles and labels
# plt.title('Line Chart with Multiple Lines')
# plt.xlabel('Number of function call sequences used')
# plt.ylabel('Opcode Coverage (%)')

# Show legend
plt.legend()

# Display the chart
# plt.show()
plt.tight_layout()
plt.savefig("SaleClockAuction.pdf")


plt.close()

# Sample data for multiple lines
x = range(1, min_length + 1)
y1 = result["./random_myth_SupeRare.log-random"]
y2 = result["./mbt_myth_SupeRare.log-mbt"]
# y1 = y1/100
# y2 = y2/100


# Create the line chart with multiple lines
plt.plot(x, y2, marker='x', linestyle='--', color='r', label='Mythril-SMCon')
plt.plot(x, y1, marker='o', linestyle='-', color='b', label='Mythril-Random')

# Add titles and labels
# plt.title('Line Chart with Multiple Lines')
# plt.xlabel('Number of function call sequences used')
# plt.ylabel('Opcode Coverage (%)')

# Show legend
plt.legend()

# Display the chart
# plt.show()
plt.tight_layout()
plt.savefig("SupeRare.pdf")
