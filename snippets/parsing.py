import subprocess
from os.path import join as pj

def pcap2csv(folder, filename="output.csv"):
    """
    Execute a simple filter on PCAP and count
    """
    # Getting raw data
    with open(pj(folder, filename), "w") as f:

        command = ["tshark",
                   "-T", "fields",
                   "-E", "header=y",
                   "-E", "separator=,",
                   "-Y", "udp || icmpv6",
                   "-e", "frame.time_epoch",
                   "-e", "frame.protocols",
                   "-e", "frame.len",
                   "-e", "wpan.fcs",
                   "-e", "wpan.seq_no",
                   "-e", "wpan.src16",
                   "-e", "wpan.dst16",
                   "-e", "wpan.src64",
                   "-e", "wpan.dst64",
                   "-e", "icmpv6.type",
                   "-e", "ipv6.src",
                   "-e", "ipv6.dst",
                   "-e", "icmpv6.code",
                   "-e", "udp.dstport",
                   "-e", "udp.srcport",
                   "-e", "data.data",
                   "-r", pj(folder, "output.pcap")]

        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        f.write(stdout)
