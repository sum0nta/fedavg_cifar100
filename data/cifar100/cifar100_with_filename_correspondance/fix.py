
filename = 'federated_train_alpha_0.50_with_name.csv'
line = 1

with open(filename) as f:
    data = f.read().splitlines() # Read csv file
with open(filename, 'w') as g:
    g.write('\n'.join([data[:line]] + data[line+1:])) # Write to file
