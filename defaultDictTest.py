from collections import defaultdict

something = 'that'
def test1():

	print(10)
def test2():
	print(20)
options = defaultdict(lambda: test2, {'this': test1, 'that': test2, 'there': test1})

options[something]()

    

