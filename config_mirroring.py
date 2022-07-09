from netmiko import ConnectHandler
from ipaddress import ip_interface

source = {
    'host':'192.168.8.10',
    'port':22,
    'username':'cisco',
    'password':'cisco',
    'secret':'cisco',
    'device_type':'cisco_ios'
}

destination = {
    'host':'192.168.8.11',
    'port':22,
    'username':'cisco',
    'password':'cisco',
    'secret':'cisco',
    'device_type':'cisco_ios'
}

print('Cisco Router Loopback Mirroring Program'.center(80,'*'),'\n')

try:
    src = ConnectHandler(**source) #Kaynak router'ına bağlantı satırı
    src.enable()
    
except Exception as e:
    raise(e)
    
else:
    print(f'Connecting to the device on {source["host"]}:{source["port"]} is succesfull')
    
try:
    dst = ConnectHandler(**destination) #Hedef router'ına bağlantı satırı
    dst.enable() 
    
except Exception as e:
    raise(e)
    
else:
    print(f'Connecting to the device on {destination["host"]}:{destination["port"]} is succesfull')

print('*Getting the list of loopback interfaces from source devices') #Kaynak cihazdan konf. almak için
src_interfacelo = [x['intf'] for x in src.send_command('show ip int brief', use_textfsm=True) if x ['intf'].startswitch('Loopback')

print('*Getting the list of loopback interfaces from destination devices') #Hedef cihazdan konf. almak için
src_interfacelo = [x['intf'] for x in dst.send_command('show ip int brief', use_textfsm=True) if x ['intf'].startswitch('Loopback')

commands = []
                   
print('**Generating commands to remove all loopbacks on destination device') #yukarıdan aldığımız bilgiyle hedefteki lo'
                   
for loopback_interface in dst_interfacelo:
    commands.append(f'no int {loopback_interface}')

print('**Generating commands to copy all loopbacks on source device') #kaynaktan konfigürasyon kopyalamak için
                   
for loopback_interface in src_interfacelo:
    loopback_interface_info = src.send_command(f"show int {loopback_interface}",use_textfsm=True)[0]
    
    print(' *** Generating Commands to Mirror All Loopbacks')
    commands.append(f'int {loopback_interface}')
    
    if loopback_interface_info["ip_address"]:
        ip = ip_interface(loopback_interface_info["ip_address"])
        commands.append(f'ip address {ip.ip.compressed} {ip.netmask.compressed}')
    
    if loopback_interface_info['description']:
        commands.append(f'desc {loopback_interface_info["description"]}')
    
    commands.append('exit')
                   
print('Commands'.center(80,'*'))

for command in commands:
    print(command)
print(''.center(80,'-'))

print(' *** Running commands on destination devices')
dst.send_config_set(commands)
