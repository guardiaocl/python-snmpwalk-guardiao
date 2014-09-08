#sudo pip install pysnmp pysnmp-mibs

import urllib2,time
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.smi import builder, view

__author__ = 'Guardiao Cloud'

mibBuilder = builder.MibBuilder().loadModules('IP-MIB')
mibView = view.MibViewController(mibBuilder)

apiKey = "xxxxxxxx-yyyy-zzzz-wwww-kkkkkkkkkkkk" #@todo Alterar Numero da API Key
serialKey = "GUC0001" #@todo Alterar numero de serie do dispositivo de Coleta
checkedTime = 5

snmpPort = 161 #@todo Alterar porta do SNMP
snmpIP = '127.0.0.1' #@todo Alterar IP da maquina com SNMP
snmpCommunity = 'public' #@todo Alterar comunidade padrao SNMP
snmpInterface = 'eth0' #@todo Alterar interface de Rede que se deseje monitorar

lastValueIn = 0
lastValueOut = 0
valorRef = False
tempoIncial = time.time()

if __name__ == '__main__':
    while True:
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBindTable = cmdGen.nextCmd(
            cmdgen.CommunityData(snmpCommunity, mpModel=0),
            cmdgen.UdpTransportTarget((snmpIP, snmpPort)),
            cmdgen.MibVariable('IF-MIB', 'ifDescr'),
            cmdgen.MibVariable('IF-MIB', 'ifInOctets'),
            cmdgen.MibVariable('IF-MIB', 'ifOutOctets'),
        )

        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
                    )
                )
            else:
                for varBindTableRow in varBindTable:
                    controle = False
                    consumoIn = 0
                    consumoOut = 0
                    for oid, val in varBindTableRow:
                        if val.prettyPrint() == snmpInterface and controle == False :
                            controle = True
                        if controle:
                            oid, label, suffix = mibView.getNodeName(oid)
                            oidLabel = label[len(label)-1]
                            if(oidLabel == 'ifInOctets'):
                                actualInVal = float(val.prettyPrint())
                                consumoIn = (((lastValueIn - actualInVal) * 8)/(tempoIncial - time.time()))/1024
                                lastValueIn = float(val.prettyPrint())
                            if(oidLabel == 'ifOutOctets'):
                                actualOutVal = float(val.prettyPrint())
                                consumoOut = (((lastValueOut - actualOutVal) * 8)/(tempoIncial - time.time()))/1024
                                lastValueOut = float(val.prettyPrint())
                if valorRef == True :
                    valorEnvio = "bandwidthEntrada={0}&bandwidthSaida={1}".format(int(round(consumoIn)),int(round(consumoOut)))
                    url = "http://guardiao.cl/collect/{0}/?apiKey={1}&{2}".format(serialKey,apiKey,valorEnvio)
                    print urllib2.urlopen(url).read()
                valorRef = True
        time.sleep(checkedTime)
        tempoIncial = time.time()