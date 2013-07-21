#!/usr/bin/env python

import sys, subprocess, io
cwd = sys.path[0]

sys.path.append(cwd+'/lib/python-gnupg-0.3.3')
import gnupg

class TrollWoT_ASCIISign:
    def __init__(self, filename, target_keyid, homedir):
        self.target_keyid = keyid
        self.homedir = homedir
        self.keyserver_url = "http://pgp.mit.edu:11371/pks/lookup?op=vindex&search=0x{0}".format(keyid)
        self.fingerprints = [self.target_keyid]

        self.gpg = gnupg.GPG(gnupghome=homedir, gpgbinary=cwd+'/lib/gnupg/g10/gpg', verbose=False)
    
        # download target key
        print 'Downloading key {0} from pgp.mit.edu'.format(keyid)
        self.recv_key(self.target_keyid)
        
        # generate new keys
        self.gen_keys_and_sign(filename)

        # show fingerprints with gpg
        subprocess.Popen(['gpg', '--homedir', self.gpg.gnupghome, '--list-sigs', self.target_keyid]).wait()

        # prompt for uploading to key server
        upload_keys = ''
        while upload_keys != 'YES' and upload_keys != 'no':
            upload_keys = raw_input('Does this look good? Type "YES" to upload, "no" to quit: ')

        if upload_keys == 'YES':
            print 'Uploading fingerprints'
            for fingerprint in self.fingerprints:
                self.send_key(fingerprint)

            print '\n\nView the ASCII signed key here: {0}'.format(self.keyserver_url)

    def gen_keys_and_sign(self, filename):
        fingerprints_to_sign = []

        for userid in open(filename, 'r').read().strip().split('\n'):
            fingerprint = self.gen_key(userid)
            fingerprints_to_sign.append(fingerprint)
            self.fingerprints.append(fingerprint)
        
        for fingerprint in fingerprints_to_sign:
            self.sign_key(fingerprint)

    def gen_key(self, userid):
        print 'Generating key with userid: {0}'.format(userid)
        input = self.gpg.gen_key_input(name_real = userid, key_length = 4096)
        input_lines = input.split('\n')
        input = ''
        for line in input_lines:
            if 'Name-Comment' not in line and 'Name-Email' not in line:
                input += line+'\n'
        key = self.gpg.gen_key(input)
        return key.fingerprint

    def sign_key(self, signing_fingerprint):
        keyid = signing_fingerprint[-8:]
        print 'Signing key {0} with key {1}'.format(self.target_keyid, keyid)
        subprocess.Popen(['gpg', '--homedir', self.gpg.gnupghome, '--yes', '--default-key', keyid, '--sign-key', self.target_keyid]).wait()

    def recv_key(self, fingerprint):
        keyid = fingerprint[-8:]
        print 'Receiving key {0} from pgp.mit.edu'.format(keyid)
        subprocess.Popen(['gpg', '--homedir', self.gpg.gnupghome, '--keyserver', 'pgp.mit.edu', '--recv-keys', keyid]).wait()

    def send_key(self, fingerprint):
        keyid = fingerprint[-8:]
        print 'Sending key {0} to pgp.mit.edu'.format(keyid)
        subprocess.Popen(['gpg', '--homedir', self.gpg.gnupghome, '--keyserver', 'pgp.mit.edu', '--send-key', keyid]).wait()

if __name__ == '__main__':
    # arguments
    if len(sys.argv) != 3:
        print 'Usage: {0} [ascii_art.txt] [keyid]'.format(sys.argv[0])
        sys.exit()
    filename = sys.argv[1]
    keyid = sys.argv[2]

    ascii_sign = TrollWoT_ASCIISign(filename, keyid, homedir=cwd+'/homedir_ascii_sign')
