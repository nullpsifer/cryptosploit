from modules.abstractModule import *
from sslyze import *

class ExampleModule(AbstractModule):

    name = "tls_cipher_scan"

    description = "Scans host for supported TLS cipher suites."

    arguments = [
            ModuleArgumentDescription("host", "Host to scan.", True),
            ModuleArgumentDescription("port", "TLS port.", True, defaultValue=443),
        ]

    def execute(self):
        host = self.get_argument_value('host')
        port = self.get_argument_value('port')

        # Motivated by example code from
        # https://nabla-c0d3.github.io/sslyze/documentation/running-a-scan-in-python.html#full-example
        #
        try:
            all_scan_requests = [
                ServerScanRequest(server_location=ServerNetworkLocation(hostname=host, port=port))
            ]
        except ServerHostnameCouldNotBeResolved:
            print("Error resolving hostname.")
            return

        scanner = Scanner()
        scanner.queue_scans(all_scan_requests)

        server_scan_result = next(scanner.get_results())
        print(f"\n\nScanning {server_scan_result.server_location.hostname}...")

        if server_scan_result.scan_status == ServerScanStatusEnum.ERROR_NO_CONNECTIVITY:
            print(
                f"\nError: Could not connect to {server_scan_result.server_location.hostname}:"
                f" {server_scan_result.connectivity_error_trace}"
            )
            return

        # Process the result of the SSL 2.0 scan command
        ssl2_attempt = server_scan_result.scan_result.ssl_2_0_cipher_suites
        if ssl2_attempt.status == ScanCommandAttemptStatusEnum.ERROR:
            _print_failed_scan_command_attempt(ssl2_attempt)
        elif ssl2_attempt.status == ScanCommandAttemptStatusEnum.COMPLETED:
            ssl2_result = ssl2_attempt.result
            print("\nAccepted cipher suites for SSL 2.0:")
            for accepted_cipher_suite in ssl2_result.accepted_cipher_suites:
                print(f"-> {accepted_cipher_suite.cipher_suite.name}")

        # Process the result of the TLS 1.3 scan command
        tls1_3_attempt = server_scan_result.scan_result.tls_1_3_cipher_suites
        if tls1_3_attempt.status == ScanCommandAttemptStatusEnum.ERROR:
            _print_failed_scan_command_attempt(ssl2_attempt)
        elif tls1_3_attempt.status == ScanCommandAttemptStatusEnum.COMPLETED:
            tls1_3_result = tls1_3_attempt.result
            print("\nAccepted cipher suites for TLS 1.3:")
            for accepted_cipher_suite in tls1_3_result.accepted_cipher_suites:
                print(f"-> {accepted_cipher_suite.cipher_suite.name}")