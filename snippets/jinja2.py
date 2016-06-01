with open(pj(path, "main.csc"), "w") as f:
    f.write(main_csc_template.render(
        title="Dummy Simulation",
        random_seed=12345,
        transmitting_range=42,
        interference_range=42,
        success_ratio_tx=1.0,
        success_ratio_rx=1.0,
        mote_types=[
            {"name": "server", "description": "server",
                "firmware": "dummy-server.wismote"},
            {"name": "client", "description": "client",
                "firmware": "dummy-client.wismote"}
        ],
        motes=[
            {"mote_id": 1, "x": 0, "y": 0, "z": 0, "mote_type": "server"},
            {"mote_id": 2, "x": 1, "y": 1, "z": 0, "mote_type": "client"},
        ],
        script=script))
