def _coap_process(dest, sleep_time=2):
    while True:
        subprocess.call(["coap", "get", dest])
        sleep(sleep_time)

def _tunslip():
    subprocess.call(["make", "connect-router-cooja"], cwd=path)

def _run_cooja():
    subprocess.call(["make", "run"], cwd=path)

def launch_exp(timeout=100, destination="coap://example"):
    processes = {
        "cooja": Process(target=_run_cooja),
        "tunslip": Process(target=_tunslip),
        "traffic": Process(target=_coap_process,
                           args=(dest,)),
    }
    processes["cooja"].start()
    sleep(15)
    processes["tunslip"].start()
    sleep(10)
    processes["traffic"].start()

    processes["cooja"].join(timeout)
    for name, p in processes.items():
        if p.is_alive():
            print("Terminating %s" % name)
            p.terminate()
