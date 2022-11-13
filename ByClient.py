import socket
import ssl
import base64

class ByClient:
    def __init__(self) -> None:

        self.endMSG = '\r\n.\r\n'
        self.HELOcommand = 'HELO Alice\r\n'
        self.MAIL_FROMcommand = None
        self.RCPT_TOcommand = None
        self.DATAcommand = 'DATA\r\n'
        self.QUITcommand = 'QUIT\r\n'
        self.TSL = 'STARTTLS\r\n'

        # self.tsl_cxt = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

        self.fromAddress = None
        self.toAddress = None
        self.subject = None
        self.username = None
        self.passkey = None
        self.body = None


    def get_massage(self, massage):
        '''get the massage'''
        self.toAddress = [s for s in massage['toAddress'].split(';\n')]
        self.fromAddress = massage['fromAddress']
        self.subject = massage['subject']
        self.username = str(base64.b64encode(massage['fromAddress'].encode()),'utf-8')
        self.passkey = str(base64.b64encode(massage['passkey'].encode()),'utf-8')
        self.body = massage['body']

        # self.context = ssl.create_default_context()
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        self.context.check_hostname = False

    

    def send_an_email(self, mail_server = "smtp.qq.com", serverPort = 587):
        '''build connection with the server, then send the massage, free connection. '''
        '''please be sure all ready to send an email! '''

        self.mail_server = mail_server
        self.server_port = serverPort

        # build connection
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((mail_server,serverPort))
        # sock = socket.create_connection((mail_server,serverPort))
        clientSocket = self.context.wrap_socket(clientSocket,server_hostname=mail_server)

        recv0 = clientSocket.recv(1024).decode()
        print('recv0:{}'.format(recv0))
        if '220'!= recv0[:3]:
            print('220 reply not received from server!\n')
            return -1
        # end build

        
        # HELO
        clientSocket.send(self.HELOcommand.encode())

        recv1 = clientSocket.recv(1024).decode()
        print('recv1:{}'.format(recv1))
        if '250'!= recv1[:3]:
            print('220 reply not received from server!\n')
            return -2
        # end HELO


        # try to login
        clientSocket.sendall('AUTH LOGIN\r\n'.encode())
        recv2 = clientSocket.recv(1024).decode()
        print(recv2)
        if '334' != recv2[:3]:
            print('334 reply not received from server.')
            return -3

        clientSocket.sendall((self.username + '\r\n').encode())
        recvName = clientSocket.recv(1024).decode()
        print(recvName)
        if '334' != recvName[:3]:
            print('334 reply not received from server')
            return -3

        clientSocket.sendall((self.passkey + '\r\n').encode())
        recvPass = clientSocket.recv(1024).decode()
        print(recvPass)
        if '235' != recvPass[:3]:
            print('235 reply not received from server')
            return -3
        # end login


        # mail from 
        self.MAIL_FROMcommand = 'MAIL FROM: <' + self.fromAddress + '>\r\n'
        clientSocket.send(self.MAIL_FROMcommand.encode())
        recv3 = clientSocket.recv(1024).decode()
        print('recv3:{}'.format(recv3))
        if recv3[:3] != '250':
            print('250 reply not received from server.')
            return -4
        # end mail from
        
        
        # rcpt to
        for to_address in self.toAddress:
            self.RCPT_TOcommand = 'RCPT TO: <' + to_address + '>\r\n'
            clientSocket.send(self.RCPT_TOcommand.encode())
            recv4 = clientSocket.recv(1024).decode()
            print('recv4:{}'.format(recv4))
            if recv4[:3] != '250':
                print('250 reply not received from server.')
                return -5
        # end rcpt to


        # data
        clientSocket.send(self.DATAcommand.encode())
        recv5 = clientSocket.recv(1024).decode()
        print('recv5:{}'.format(recv5))
        if recv5[:3] != '354':
            print('354 reply not received from server.')
            return -6
        # end data


        # send massage
        self.massage = 'from:' + self.fromAddress + '\r\n'
        for to_address in self.toAddress:
            self.massage += 'to:' + to_address + '\r\n'
        self.massage += 'subject:' + self.subject + '\t\n'
        self.massage += '\r\n' + self.body
        clientSocket.sendall(self.massage.encode())
        #end send massage


        # endmassage
        clientSocket.send(self.endMSG.encode())
        recv6 = clientSocket.recv(1024).decode()
        print('recv6:{}'.format(recv6))
        if recv6[:3] != '250':
            print('250 reply not received from server.')
            return -7
        # end endmassage


        # quit
        clientSocket.send(self.QUITcommand.encode())
        recv7 = clientSocket.recv(1024).decode()
        print('recv7:{}'.format(recv7))
        if recv7[:3] != '221':
            print('221 reply not received from server.')
            return -8
        # end quit

        clientSocket.close()
        return 0