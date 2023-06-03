import requests
import socket
import threading
import queue
import signal
from rich.console import Console

console = Console()


def run(count, output, proxy, threads, time):
    relays = get(proxy)

    console.print("\n[bold cyan]Checking relays...[/bold cyan]\n")
    rfc = int(len(relays["relays"]) / threads)  # relays for checker
    rfct = rfc  # (temp)

    qe = queue.Queue()
    work_relays = []
    ths = []  # Threads info
    global stop_flag
    stop_flag = False

    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT, service_shutdown)

    while rfc <= len(relays["relays"]):
        th = threading.Thread(
            target=check,
            args=(
                relays["relays"][rfc - rfct:rfc],
                qe,
                time,
            ),
        )
        ths.append(th)
        th.start()
        rfc += rfct

    while True:
        wr = qe.get()
        work_relays.append(wr)
        if len(work_relays) >= count:

            for i in ths:
                stop_flag = True
                i.join()

            console.print("\n")
            if output is None:
                console.print("[i]Your relays[/i]\n")
                for i in work_relays:
                    console.print(f"Bridge {i['or_addresses'][0]} {i['fingerprint']}")
                console.print("UseBridges 1")
            else:
                with open(output, "w") as file:
                    output_text = ""
                    for i in work_relays:
                        output_text += f"Bridge {i['or_addresses'][0]} {i['fingerprint']}\n"
                    output_text += "UseBridges 1"
                    file.write(output_text)
                console.print(f"[i]Relays are saved to a file [u]{output}[/u][/i]")

            return


def get(proxy):
    if proxy is not None:
        proxy = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    baseurl = "https://onionoo.torproject.org/details?type=relay&running=true&fields=fingerprint,or_addresses"
    # Use public CORS proxy as a regular proxy in case if onionoo.torproject.org is unreachable
    urls = (
        baseurl,
        "https://corsbypasser.herokuapp.com/" + baseurl,
        "https://corsanywhere.herokuapp.com/" + baseurl,
        "https://tauron.herokuapp.com/" + baseurl,
        "https://cors-anywhere2.herokuapp.com/" + baseurl,
    )

    for url in urls:
        try:
            req = requests.get(url, proxies=proxy, timeout=5).json()
            console.print(f"[bold green]Success[/bold green]: {url}")
            return req
        except:
            console.print(f"[bold red]Failed[/bold red]: {url}")


def check(relays, qe, time):
    for j in relays:
        for i in j["or_addresses"]:
            if stop_flag:
                return
            temp = i.split(":")
            if "[" in temp[0]:
                # console.print("Ipv6 detected... Miss")
                break
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(time)
                sock.connect((temp[0], int(temp[1])))
                console.print(f"{i} - [bold green]Success[/bold green]")
                sock.close()
                qe.put_nowait(j)
            except:
                console.print(f"{i} - [bold red]Failed[/bold red]")
                sock.close()
                pass


def service_shutdown(signum, frame):
    global stop_flag
    stop_flag = True
    console.print("[bold red]\nSTOPING[/bold red]\n"*3)
    exit(0)
