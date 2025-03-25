#!/usr/bin/env python3
"""
SSL/TLS Certificate Inspector - A GUI tool to analyze domain certificates

Author: Balaji "Abi" Abishek

Why build this?
- Many devs deploy sites without checking cert configurations
- Expired/misconfigured certs are low-hanging fruit for attackers
- Manual openssl commands are tedious - this automates the checks
- Perfect for bug bounty hunters and sysadmins doing quick audits

Features:
- Checks expiration, issuer, and cipher strength
- Detects self-signed certificates
- Exports clean JSON reports
- Built with PySimpleGUI for a clean interface
"""

import requests
import ssl
import socket
import json
from datetime import datetime
import PySimpleGUI as sg
from concurrent.futures import ThreadPoolExecutor

# API endpoints
CRTSH_URL = "https://crt.sh/?q={}&output=json"
SSL_MATE_URL = "https://api.certspotter.com/v1/issuances?domain={}"

# Configure the GUI theme
sg.theme("DarkGrey5")

# Cache to avoid duplicate API calls
cert_cache = {}

def get_cert_info(domain):
    """Fetch live certificate details directly from the server"""
    if domain in cert_cache:
        return cert_cache[domain]

    context = ssl.create_default_context()
    with socket.create_connection((domain, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as ssock:
            cert = ssock.getpeercert()

    # Parse the messy cert format into something readable
    issuer = dict(x[0] for x in cert["issuer"])
    subject = dict(x[0] for x in cert["subject"])
    
    cert_info = {
        "domain": domain,
        "issuer": issuer.get("organizationName", "Unknown"),
        "valid_from": cert["notBefore"],
        "valid_to": cert["notAfter"],
        "serial_number": cert.get("serialNumber", "N/A"),
        "is_self_signed": issuer == subject,
    }
    
    cert_cache[domain] = cert_info
    return cert_info

def check_cert_transparency(domain):
    """Check Certificate Transparency logs for historical certs"""
    try:
        response = requests.get(CRTSH_URL.format(domain), timeout=10)
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        print(f"CT log error: {e}")
        return []

def analyze_cipher_strength(domain):
    """Quick check for obviously weak protocols"""
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cipher = ssock.cipher()
                return {
                    "cipher_name": cipher[0],
                    "protocol": cipher[1],
                    "bits": cipher[2],
                    "is_weak": "RC4" in cipher[0] or "DES" in cipher[0] or cipher[2] < 128
                }
    except Exception as e:
        print(f"Cipher check failed: {e}")
        return None

def days_until_expiry(expiry_date):
    """Calculate how many days until certificate expires"""
    expiry = datetime.strptime(expiry_date, "%b %d %H:%M:%S %Y %Z")
    return (expiry - datetime.utcnow()).days

def build_gui():
    """Create the main application window"""
    layout = [
        [sg.Text("SSL/TLS Certificate Inspector", font=("Helvetica", 16))],
        [sg.Text("Enter domain (e.g., example.com):")],
        [
            sg.Input(key="-DOMAIN-", size=(40, 1)),
            sg.Button("Scan", bind_return_key=True),
            sg.Button("Clear")
        ],
        [sg.HorizontalSeparator()],
        [sg.Multiline(
            key="-OUTPUT-", 
            size=(60, 15), 
            font=("Courier", 10),
            autoscroll=True,
            disabled=True
        )],
        [
            sg.Button("Export JSON"),
            sg.Button("Check Ciphers"),
            sg.Exit()
        ]
    ]
    
    return sg.Window("SSL Inspector", layout, finalize=True)

def main():
    window = build_gui()
    
    while True:
        event, values = window.read()
        
        if event in (sg.WIN_CLOSED, "Exit"):
            break
            
        if event == "Clear":
            window["-DOMAIN-"].update("")
            window["-OUTPUT-"].update("")
            continue
            
        domain = values["-DOMAIN-"].strip()
        if not domain:
            sg.popup_error("Please enter a domain first!")
            continue
            
        if event == "Scan":
            window["-OUTPUT-"].update("Scanning...\n")
            
            # Run scans in parallel for better UX
            with ThreadPoolExecutor() as executor:
                cert_future = executor.submit(get_cert_info, domain)
                ct_future = executor.submit(check_cert_transparency, domain)
                
                cert_info = cert_future.result()
                ct_logs = ct_future.result()
            
            # Build the results display
            output = []
            output.append(f"=== Certificate Details for {domain} ===\n")
            output.append(f"Issuer: {cert_info['issuer']}")
            output.append(f"Valid From: {cert_info['valid_from']}")
            output.append(f"Expires On: {cert_info['valid_to']}")
            
            days_left = days_until_expiry(cert_info["valid_to"])
            expiry_status = "✅" if days_left > 30 else "⚠️" if days_left > 0 else "❌"
            output.append(f"Status: {expiry_status} {days_left} days remaining")
            
            if cert_info["is_self_signed"]:
                output.append("\n⚠️ WARNING: Self-signed certificate detected!")
            
            if ct_logs:
                output.append(f"\nFound {len(ct_logs)} historical certificates in CT logs")
            
            window["-OUTPUT-"].update("\n".join(output))
            
        elif event == "Check Ciphers":
            cipher_info = analyze_cipher_strength(domain)
            if cipher_info:
                output = window["-OUTPUT-"].get()
                output += "\n=== Cipher Analysis ===\n"
                output += f"Protocol: {cipher_info['protocol']}\n"
                output += f"Cipher: {cipher_info['cipher_name']} ({cipher_info['bits']} bits)\n"
                
                if cipher_info["is_weak"]:
                    output += "❌ WEAK CIPHER DETECTED - Consider upgrading!\n"
                else:
                    output += "✅ Cipher strength appears secure\n"
                
                window["-OUTPUT-"].update(output)
        
        elif event == "Export JSON":
            cert_info = get_cert_info(domain)
            cipher_info = analyze_cipher_strength(domain)
            ct_logs = check_cert_transparency(domain)
            
            report = {
                "domain": domain,
                "certificate": cert_info,
                "cipher": cipher_info,
                "ct_log_entries": len(ct_logs),
                "scan_time": datetime.utcnow().isoformat()
            }
            
            filename = f"ssl_report_{domain.replace('.', '_')}.json"
            with open(filename, "w") as f:
                json.dump(report, f, indent=2)
            
            sg.popup(f"Report saved to {filename}", title="Export Complete")

    window.close()

if __name__ == "__main__":
    main()
