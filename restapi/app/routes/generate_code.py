import string
import random

class ReedeemCode(object):
	def __init__(self, app=None):
		super(ReedeemCode, self).__init__()
		self.arr = []
		self.dict = {}
		
	def string_generator(self, size):
		chars = string.ascii_uppercase + string.ascii_lowercase
		return ''.join(random.choice(chars) for _ in range(size))
 
	def string_num_generator(self, size):
		chars = string.ascii_lowercase + string.digits
		return ''.join(random.choice(chars) for _ in range(size))

	def generate_code(self):
		try:
			with open('redeem.txt') as f:
				for line in f.readlines():
					code = line.replace('\n', '')
					self.dict[code] = 1
			f.close()
			
			with open('redeem.txt', 'a') as f:
				for i in range(0, 500):
					code = self.string_num_generator(2) + self.string_generator(2) + self.string_num_generator(2) + self.string_generator(2)
					if code not in self.dict:
						self.arr.append(code)
						f.write('{}\n'.format(code))

					if len(self.arr) == 500:
						break

			f.close()
			print self.arr
			
		except Exception as ex:
			print(str(ex))

if __name__ == '__main__':
	r = ReedeemCode()
	r.generate_code()