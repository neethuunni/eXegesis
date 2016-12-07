check = False
def test(value):
	global check
	if value % 3 == 0:
		check = True
	print check
	value += 1
	if check!= 5:
		test(check)
test(1)