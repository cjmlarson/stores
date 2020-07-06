import csv
import statistics
import matplotlib.pyplot as plt
from scipy import stats as stats

# read in data
data = list(csv.reader(open('output.csv')))
data.pop(0)

# set up variables
num_stores = int(len(data) / 12)
revenues = [0] * num_stores
net_costs = [0] * num_stores

# sum annual revenues and costs
for row in data:
    revenues[int(row[0]) - 1] += float(row[3])
    net_costs[int(row[0]) - 1] += float(row[4]) + float(row[5]) + float(row[6])

# find annual profit margins
margins = []
for i in range(num_stores):
    margins.append((revenues[i] - net_costs[i]) / revenues[i])

# find mean and median
mean = statistics.mean(margins)
median = statistics.median(margins)
print("Mean = %.1f%%" % (mean * 100))
print("Median = %.1f%%" % (median * 100))

# plot histogram
plt.hist(margins, bins=15)
plt.title("Adjusted profit margins")
plt.savefig("hist_adj.png")
plt.close()

# plot box plot
plt.boxplot(margins, vert=False)
plt.title("Adjusted profit margins")
plt.savefig("box_adj.png")
plt.close()

# plot qq plot
stats.probplot(margins, dist="norm", plot=plt)
plt.savefig("qq_adj.png")
plt.close()

# check Shapiro-Wilk test
print("\nS-W test: reject (p = %.1e)" % stats.shapiro(margins)[1])
print("The profit margins do not appear normally distributed.")

# find monthly and quarterly aggregate revenues
monthly_revs = [0] * 12
quarterly_revs = [0] * 4

for row in data:
    monthly_revs[int(row[1]) - 1] += float(row[3]) / (10 ** 9)
    quarterly_revs[int((int(row[1]) - 1) / 3)] += float(row[3]) / (10 ** 9)

# plot monthly revenues
labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
plt.bar(labels, monthly_revs)
plt.title("Monthly aggregate adjusted revenues")
plt.ylabel("Revenue ($ in Billions)")
plt.ticklabel_format(style='plain', axis='y')
plt.savefig("months_adj.png")
plt.close()

# plot monthly deviations
mean = statistics.mean(monthly_revs)
devs = []
for i in monthly_revs:
    devs.append(100 * (i - mean) / mean)
plt.bar(labels, devs)
plt.title("Monthly adjusted revenues - deviation from mean")
plt.ylabel("% deviation")
plt.ticklabel_format(style='plain', axis='y')
plt.savefig("month_devs_adj.png")
plt.close()

# plot quarterly revenues
labels = ["Q1", "Q2", "Q3", "Q4"]
plt.bar(labels, quarterly_revs)
plt.title("Quarterly aggregate adjusted revenues")
plt.ylabel("Revenue ($ in Billions)")
plt.ticklabel_format(style='plain', axis='y')
plt.savefig("quarters_adj.png")
plt.close()

# plot quarterly deviations
mean = statistics.mean(quarterly_revs)
devs = []
for i in quarterly_revs:
    devs.append(100 * (i - mean) / mean)
plt.bar(labels, devs)
plt.title("Quarterly adjusted revenues - deviation from mean")
plt.ylabel("% deviation")
plt.ticklabel_format(style='plain', axis='y')
plt.savefig("quarter_devs_adj.png")
plt.close()
