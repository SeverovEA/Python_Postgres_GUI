import bcrypt

word = '123'
word = word.encode('utf-8')
slt = bcrypt.gensalt()
hashed = bcrypt.hashpw(word, slt)
print(hashed)
