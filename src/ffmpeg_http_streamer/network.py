import ipaddress
import socket

import psutil


def is_private_ip(ip_address):
    try:
        ip_obj = ipaddress.ip_address(ip_address)

    except ValueError:
        return False

    else:
        return ip_obj.is_private and not ip_obj.is_loopback


def get_private_ip():
    ethernet_ids = ["eth", "enp", "ens", "eno", "ethernet"]
    wifi_ids = ["wlan", "wl", "wi-fi", "wifi", "wireless"]

    all_interfaces = psutil.net_if_addrs()
    interface_stats = psutil.net_if_stats()

    for interface_name, interface_addresses in all_interfaces.items():
        if (
            interface_name not in interface_stats
            or not interface_stats[interface_name].isup
        ):
            continue

        lower_name = interface_name.lower()
        if any(lower_name.startswith(id_str) for id_str in ethernet_ids):
            for addr in interface_addresses:
                if addr.family == socket.AF_INET and is_private_ip(addr.address):
                    return addr.address

    for interface_name, interface_addresses in all_interfaces.items():
        if (
            interface_name not in interface_stats
            or not interface_stats[interface_name].isup
        ):
            continue

        lower_name = interface_name.lower()
        if any(id_str in lower_name for id_str in wifi_ids):
            for addr in interface_addresses:
                if addr.family == socket.AF_INET and is_private_ip(addr.address):
                    return addr.address

    for interface_name, interface_addresses in all_interfaces.items():
        if (
            interface_name not in interface_stats
            or not interface_stats[interface_name].isup
        ):
            continue

        for addr in interface_addresses:
            if addr.family == socket.AF_INET and is_private_ip(addr.address):
                return addr.address

    return None


def is_port_free(private_ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.bind((private_ip, port))
        except OSError:
            return False
        else:
            return True
