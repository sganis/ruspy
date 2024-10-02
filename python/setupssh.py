# Golddrive
# 09/08/2018, San
# setup ssh keys

import os
import paramiko
import logging
import subprocess
import re
import time
from enum import Enum

logger = logging.getLogger('cenop')
logging.getLogger("paramiko.transport").setLevel(logging.WARNING)

DIR = os.path.dirname(os.path.realpath(__file__))

def run(cmd, capture=False, detach=False, shell=True, timeout=30):
	cmd = re.sub(r'[\n\r\t ]+',' ', cmd).replace('  ',' ').strip()
	header = 'CMD'
	if shell:
		header += ' (SHELL)'
	logger.debug(f'{header}: {cmd}')
	r = subprocess.CompletedProcess(cmd, 0)
	r.stdout = ''
	r.stderr = ''
	try:
		r = subprocess.run(cmd, capture_output=capture, shell=shell, 
					timeout=timeout, text=True)
	except Exception as ex:
		r.stderr = repr(ex)
		logger.error(r)
		return r

	if r.returncode != 0:
		if r.stderr and r.stderr.startswith('Warning'):
			logger.warning(r)
		else:
			logger.error(r)		
	if capture:
		r.stdout = r.stdout.strip()
		r.stderr = r.stderr.strip()
	return r
	
def get_app_key(user):

	return f'{ os.path.expandvars("%USERPROFILE%") }\\.ssh\\id_rsa'
	
def testhost(userhost, port=22):
	'''
	Test if host respond to port
	Return: True or False
	'''
	logger.debug(f'Testing port {port} at {userhost}...')
	user, host = userhost.split('@')
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	rb = ''
	try:
		client.connect(hostname=host, username=user, password='', port=port, timeout=5)	
		rb = 'OK'
	except (paramiko.ssh_exception.AuthenticationException,
		paramiko.ssh_exception.BadAuthenticationType,
		paramiko.ssh_exception.PasswordRequiredException):
		rb = 'OK'
	except Exception as ex:
		rb = 'BAD_HOST'
		logger.error(ex)
	finally:
		client.close()
	return rb


def testssh(userhost, port=22):
	'''
	Test ssh key authentication
	'''
	user, host = userhost.split('@')
	seckey = get_app_key(user)
	logger.debug(f'Testing ssh keys for {userhost} using key {seckey}...')
	
	rb = testhost(userhost, port)
	if rb == 'BAD_HOST':
		return rb
	
	if not os.path.exists(seckey):
		seckey_win = seckey.replace('/','\\')
		logger.error(f'Key does not exist: {seckey_win}')
		rb = 'BAD_LOGIN'
		return rb

	logger.debug(f'Logging in with keys for {userhost}...')
	rb = ''
	
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	k = paramiko.RSAKey.from_private_key_file(seckey)
	try:
		client.connect(hostname=host, username=user, port=port, timeout=10, pkey=k)
		rb = 'OK'
	except (paramiko.ssh_exception.AuthenticationException,
		paramiko.ssh_exception.BadAuthenticationType,
		paramiko.ssh_exception.PasswordRequiredException) as ex:
		rb = 'BAD_LOGIN'
		logger.error(ex)
	except Exception as ex:
		rb = 'BAD_HOST'
		logger.error(ex)
	finally:
		client.close()
	return rb

def generate_keys(userhost):
	logger.debug('Generating new ssh keys...')
	user, host = userhost.split('@')
	seckey = get_app_key(user)
	pubkey = f'{seckey}.pub'
	now = time.time()
	if os.path.exists(seckey):
		os.rename(seckey, f'{seckey}.{ now }.bak')
	if os.path.exists(pubkey):
		os.rename(pubkey, f'{pubkey}.{ now }.bak')
	rb = ''
	
	# use ssh-keygen
	# print(run('where ssh-keygen'))
	# cmd = f'echo y |ssh-keygen -q -N "" -f {seckey} -b 2048 -t rsa -m PEM'
	# ssh-keygen defaults to openssh rsa 3072 bits keys
	# PEM format not supported by libssh2 openssl no-stdio ?
	cmd = f'echo y |ssh-keygen -m PEM -q -N "" -f {seckey}'
	run(cmd)
	with open(pubkey) as r:
		pubkey = r.read()

	# use paramiko
	# sk = paramiko.RSAKey.generate(2048)
	# try:
	# 	sshdir = os.path.dirname(seckey)
	# 	if not os.path.exists(sshdir):
	# 		os.makedirs(sshdir)
	# 		os.chmod(sshdir, 0o700)
	# 	sk.write_private_key_file(seckey)	
	# except Exception as ex:
	# 	logger.error(f'{ex}, {seckey}')
	# 	rb.error = str(ex)
	# 	return rb	
	# pubkey = f'ssh-rsa {sk.get_base64()} {userhost}'
	# try:
	# 	with open(seckey + '.pub', 'wt') as w:
	# 		w.write(pubkey)
	# except Exception as ex:
	# 	msg = f'Could not save public key: {ex}'
	# 	logger.error(msg)
	# 	rb.error = msg
	# 	return rb

	rb.output = pubkey
	return rb

def has_app_keys(user):
	logger.debug('checking if user has keys...')
	seckey = get_app_key(user)
	pubkey = f'{seckey}.pub'
	output = ''
	if os.path.exists(seckey):
		try:
			sk = paramiko.RSAKey.from_private_key_file(seckey)
			output = f'ssh-rsa {sk.get_base64()}'
			if os.path.exists(pubkey):				
				with open(pubkey) as r:
					output2 = r.read()
				if output.split()[1] != output2.split()[1]:
					logger.error('public key invalid!!!!!!!!!!!!!')
					logger.error(output)
					logger.error(output2)
					output = ''
				logger.debug('current keys are ok')
		except Exception as ex:
			logger.error(ex)
	return output and output.startswith('ssh-rsa')

def set_key_permissions(user):
	logger.debug('setting ssh key permissions...')
	seckey = get_app_key(user)
	# ssh_folder = os.path.dirname(seckey)
	run(fr'icacls {seckey} /c /t /inheritance:d', capture=True)
	run(fr'icacls {seckey} /c /t /grant { os.environ["USERNAME"] }:F', capture=True)
	run(fr'icacls {seckey} /c /t /grant SYSTEM:F', capture=True)
	run(fr'icacls {seckey} /c /t /remove Administrator BUILTIN\Administrators BUILTIN Everyone Users', capture=True)
	# Verify 
	# run(fr'icacls {seckey}')
	
def main(userhost, password, port=22):
	'''Setup ssh keys, return ReturnBox'''
	logger.debug(f'Setting up ssh keys for {userhost}...')
	rb = ''
	user, host = userhost.split('@')
	seckey = get_app_key(user)	
	pubkey = ''
	if has_app_keys(user):
		logger.debug('Private key already exists.')
		sk = paramiko.RSAKey.from_private_key_file(seckey)
		pubkey = f'ssh-rsa {sk.get_base64()} {userhost}'
	else:
		rbkey = generate_keys(userhost)
		if rbkey.error:
			rbkey.returncode = 'BAD_SSH'
			return rbkey
		else:
			pubkey = rbkey.output

	# connect
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	try:
		logger.debug('Connecting using password...')
		client.connect(hostname=host, username=user, password=password, port=port, timeout=10, look_for_keys=False)     
	except paramiko.ssh_exception.AuthenticationException:
		logger.error(f'User or password wrong')
		rb = 1
	except Exception as ex:
		logger.error(f'connection error: {ex}')
		rb = 2
	if rb:
		logger.error(rb.error)
		if 'getaddrinfo failed' in rb.error:
			logger.error(f'{host} not found')
		client.close()
		rb = 'BAD_SSH'
		return rb

	set_key_permissions(user)

	logger.debug(f'Publising public key...')		
	# Copy to the target machines.
	# cmd = f"exec bash -c \"cd; umask 077; mkdir -p .ssh && echo '{pubkey}' >> .ssh/authorized_keys || exit 1\" || exit 1"
	cmd = f"exec sh -c \"cd; umask 077; mkdir -p .ssh; echo '{pubkey}' >> .ssh/authorized_keys\""
	logger.debug(cmd)
	ok = False
	
	try:
		stdin, stdout, stderr = client.exec_command(cmd, timeout=10)
		rc = stdout.channel.recv_exit_status()   
		if rc == 0:
			logger.debug('Key transfer successful')
			rb = 'OK'
		else:
			logger.error(f'Error transfering public key: exit {rc}, error: {stderr}')
	except Exception as ex:
		logger.error(ex)
		rb = 'BAD_SSH'
		logger.error(f'error transfering public key: {ex}')
		return rb
	finally:
		client.close()

	err = stderr.read()
	if err:
		logger.error(err)
		rb = 'BAD_SSH'
		logger.error(f'error transfering public key, error: {err}')
		return rb
	
	rb = testssh(userhost, port)
	if rb == 'OK':
		logger.info("SSH setup successfull.")
	else:
		message = 'SSH setup test failed'
		detail = ''
		if rb == 'BAD_LOGIN':
			detail = ': authentication probem'
		else:
			message = ': connection problem'
		rb = 'BAD_SSH'
		logger.error(message + detail)
	return rb


if __name__ == '__main__':

	import sys
	import os
	import getpass
	assert (len(sys.argv) > 2 and '@' in sys.argv[1]) # usage: prog user@host pass
	platform = 'x64'
	if 'PLATFORM' in os.environ:
		platform = os.environ['PLATFORM']
	path = os.environ['PATH']
	os.environ['PATH'] = f'{DIR};{DIR}\\..\\vendor\\{platform}\\openssh;{path}'
	userhost = sys.argv[1]
	password = sys.argv[2]
	port=22

	if ':' in userhost:
		userhost, port = userhost.split(':')                             

	logging.basicConfig(level=logging.DEBUG)
	
	user, host = userhost.split('@')
	if has_app_keys(user) and testssh(userhost, port) == 'OK':
		logger.info('SSH authentication is OK, no need to setup.')
	else:
		main(userhost, password, port)


