
FILENAME = 'federated_train_alpha_0.50_with_name.csv'
DELETE_LINE_NUMBER = 1

with open(FILENAME) as f:
    data = f.read().splitlines() # Read csv file
with open(FILENAME, 'w') as g:
    g.write('\n'.join([data[:DELETE_LINE_NUMBER]] + data[DELETE_LINE_NUMBER+1:])) # Write to file
