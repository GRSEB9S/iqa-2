import sys
from lr import LogisticRegression
#from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

X, Y = [], []
for line in sys.stdin:
	p = line.strip().split(' ')
	X.append([float(x) for x in p[1:-1]])
	Y.append(int(p[-1]))

X_train,X_test,Y_train,Y_test = train_test_split(X,Y,test_size=0.33)

W = [0] * len(X[0])
m = LogisticRegression()
W = m.fit(X_train, Y_train, W, 1.0, 50000)
print '== test on kflearn:', m.score(X_test,Y_test, W)
print '== train on kflearn:', m.score(X_train,Y_train, W)
print '== all on kflearn:', m.score(X,Y, W)

'''
m = LogisticRegression()
m.fit(X_train, Y_train)
print '== test on sklearn:', m.score(X_test,Y_test)
'''
