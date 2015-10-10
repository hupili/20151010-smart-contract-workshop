import serpent
from ethereum import tester, utils, abi
from sha3 import sha3_256
import sys
import struct
import binascii
import random

serpent_code = '''
data voter[3](address, commit, choice, has_revealed)
data num_voters
data reward
data timer_start
data check_winner=array(3)
def init():
	self.check_winner = array(3)
	check_winner[0]=0
	check_winner[1]=0
	check_winner[2]=0
	self.num_voters = 0

#accepts a hash from the voter in form sha3(address, choice, nonce)
def add_voter(voter_commitment):
	#prevents a max callstack exception
	if self.test_callstack() != 1: return(-1)

	if self.num_voters < 3 and msg.value >= 1000:
		self.reward = self.reward + msg.value
		self.voter[self.num_voters].address = msg.sender
		self.voter[self.num_voters].commit = voter_commitment
		self.num_voters = self.num_voters + 1
		if msg.value - 1000 > 0:
			send(0, msg.sender, msg.value-1000)
		return(0)
	else:	
		if msg.value > 0 :
			# prevent unnecessary leakage of money
			send(0, msg.sender, msg.value)
		return(-1)
		
#verifies the choice in their committed answer matches
def open(choice, nonce):
	if self.test_callstack() != 1: return(-1)
	#Ensure voters are in the contract
	if not num_voters == 2: return(-1)
	#Determine which voter submitted the open request

	if msg.sender == self.voter[0].address:
		voter_num = 0
	elif msg.sender == self.voter[1].address:
		voter_num = 1
	elif msg.sender == self.voter[2].address:
		voter_num = 2
	else:
		return(-1)
	#Check the commitment and ensure they have not tried to commit already
	if sha3([msg.sender, choice, nonce], items=3) == self.voter[voter_num].commit and not self.voter[voter_num].has_revealed:
		#If commitment verified, we should store choice in plain text
		self.voter[voter_num].choice = choice
		#Store current block number to give other voter 10 blocks to open their commit
		self.voter[voter_num].has_revealed = 1		
		if not self.timer_start:
			self.timer_start = block.number
		return(0)
	else:
		return(-1)
def check():
	if self.test_callstack() != 1: return(-1)
	#Check to make sure at least 10 blocks have been given for both voters to reveal their vote.
	if block.number - self.timer_start < 10: return(-2)
	#check to see if both voters have revealed answer
	if self.voter[0].has_revealed and self.voter[1].has_revealed and self.voter[2].has_revealed:
		p0_choice = self.voter[0].choice
		p1_choice = self.voter[1].choice
		p2_choice = self.voter[2].choice

		self.check_winner[p0_choice] += 1
		self.check_winner[p1_choice] += 1
		self.check_winner[p2_choice] += 1

		return(max(self.check_winner))

	else:
		return(-1)
#returns the balance to ensure funds were lost and won properly
def balance_check():
	log(self.storage["voter1"].balance)
	log(self.storage["voter2"].balance)
def test_callstack():
	return(1)
'''

s = tester.state()
c = s.abi_contract(serpent_code)

print("Output of 1 designated success for voter 1.")
print("Output of 2 designated success for voter 2.")
print("Output of 0 designated a tie.\n")
print("Output of -1 designated an error.\n")

##################################### SETUP COMMITMENTS ########################################
choice = [0,1,2]

# Use default addresses for Alice and Bob
alice = tester.a0
alice_key = tester.k0
bob = tester.a1
bob_key = tester.k1
eve = tester.a2
eve_key = tester.k2

tobytearr = lambda n, L: [] if L == 0 else tobytearr(n / 256, L - 1)+[n % 256]
zfill = lambda s: (32-len(s))*'\x00' + s

choice1 = random.randint(0,len(choice))
nonce1 = random.randint(0,2**32-1)
ch1 = ''.join(map(chr, tobytearr(choice1, 32)))
no1 = ''.join(map(chr, tobytearr(nonce1, 32)))
print("Alice chooses {} which is: {}").format(choice1, choice[choice1])



## Use Alice's address for the commitment
s1 = ''.join([zfill(alice), ch1, no1])
comm1 = utils.sha3(s1)

choice2 = random.randint(0,len(choice))
nonce2 = random.randint(0,2**32-1)
ch2 = ''.join(map(chr, tobytearr(choice2, 32)))
no2 = ''.join(map(chr, tobytearr(nonce2, 32)))
print("Bob chooses {} which is: {}\n").format(choice2, choice[choice2])

## Use Bob's address for the commitment
s2 = ''.join([zfill(bob), ch2, no2])
comm2 = utils.sha3(s2)


choice3 = random.randint(0,len(choice))
nonce3 = random.randint(0,2**32-1)
ch3 = ''.join(map(chr, tobytearr(choice3, 32)))
no3 = ''.join(map(chr, tobytearr(nonce3, 32)))
print("Eve chooses {} which is: {}").format(choice3, choice[choice3])



## Use Eve's address for the commitment
s3 = ''.join([zfill(eve), ch3, no3])
comm3 = utils.sha3(s3)

c.init()
print "good to go"
'''
o = c.add_voter(comm1, value=1000, sender=alice_key)
print("Alice Added: {}").format(o)

o = c.add_voter(comm2, value=1000, sender=bob_key)
print("Bob Added: {}\n").format(o)


o = c.add_voter(comm3, value=1000, sender=eve_key)
print("Eve Added: {}\n").format(o)

o = c.open(choice1,nonce1, sender=alice_key)
print("Open for Alice: {}").format(o)

o = c.open(choice2,nonce2, sender=bob_key)
print("Open for Bob: {}\n").format(o)


o = c.open(choice3,nonce3, sender=eve_key)
print("Open for Eve: {}\n").format(o)


s.mine(11) # needed to move the blockchain at least 10 blocks so check can run

o = c.check(sender=tester.k1)
print str(o) + "wins"
'''
#c.balance_check(sender=tester.k0)