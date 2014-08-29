import string

char_set = list(string.ascii_letters) + [str(i) for i in range(10)]

def base_62(num):
	converted = []
	while(num > 0):
		rem = num % 62
		converted.append(char_set[rem])
		num /= 62
	return ''.join(converted)